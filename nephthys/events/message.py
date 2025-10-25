import logging
from datetime import datetime
from typing import Any
from typing import Dict

from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.macros import run_macro
from nephthys.utils.env import env
from nephthys.utils.logging import send_heartbeat
from nephthys.utils.ticket_methods import delete_and_clean_up_ticket
from prisma.enums import TicketStatus

ALLOWED_SUBTYPES = ["file_share", "me_message", "thread_broadcast"]


async def on_message(event: Dict[str, Any], client: AsyncWebClient):
    """
    Handle incoming messages in Slack.
    """
    if "subtype" in event and event["subtype"] not in ALLOWED_SUBTYPES:
        return
    if "bot_id" in event:
        logging.info(f"Ignoring bot message from {event['bot_id']}")
        return

    user = event.get("user", "unknown")
    text = event.get("text", "")

    db_user = await env.db.user.find_first(where={"slackId": user})

    # Messages sent in a thread with the "send to channel" checkbox checked
    if event.get("subtype") == "thread_broadcast" and not (db_user and db_user.helper):
        await client.chat_delete(
            channel=event["channel"],
            ts=event["ts"],
            as_user=True,
            token=env.slack_user_token,
            broadcast_delete=True,
        )
        await client.chat_postEphemeral(
            channel=event["channel"],
            user=event["user"],
            text=env.transcript.thread_broadcast_delete,
            thread_ts=event["thread_ts"] if "thread_ts" in event else event["ts"],
        )

    if event.get("thread_ts"):
        if db_user and db_user.helper:
            ticket_message = await env.db.ticket.find_first(
                where={"msgTs": event["thread_ts"]},
                include={"openedBy": True, "tagsOnTickets": True},
            )
            if not ticket_message or ticket_message.status == TicketStatus.CLOSED:
                return
            first_word = text.split()[0].lower()

            if first_word[0] == "?" and ticket_message:
                await run_macro(
                    name=first_word.lstrip("?"),
                    ticket=ticket_message,
                    helper=db_user,
                    text=text,
                    macro_ts=event["ts"],
                )
            else:
                await env.db.ticket.update(
                    where={"msgTs": event["thread_ts"]},
                    data={
                        "assignedTo": {"connect": {"id": db_user.id}},
                        "status": TicketStatus.IN_PROGRESS,
                        "assignedAt": (
                            datetime.now()
                            if not ticket_message.assignedAt
                            else ticket_message.assignedAt
                        ),
                    },
                )
        return

    thread_url = f"https://hackclub.slack.com/archives/{env.slack_help_channel}/p{event['ts'].replace('.', '')}"

    db_user = await env.db.user.find_first(where={"slackId": user})
    if db_user:
        past_tickets = await env.db.ticket.count(where={"openedById": db_user.id})
    else:
        past_tickets = 0
        user_info = await client.users_info(user=user) or {}
        username = user_info.get("user", {})[
            "name"
        ]  # this should never actually be empty but if it is, that is a major issue

        if not username:
            await send_heartbeat(
                f"SOMETHING HAS GONE TERRIBLY WRONG <@{user}> has no username found - <@{env.slack_maintainer_id}>"
            )
        db_user = await env.db.user.upsert(
            where={
                "slackId": user,
            },
            data={
                "create": {"slackId": user, "username": username},
                "update": {"slackId": user, "username": username},
            },
        )

    user_info_response = await client.users_info(user=user) or {}
    user_info = user_info_response.get("user")
    profile_pic = None
    display_name = "Explorer"
    if user_info:
        profile_pic = user_info["profile"].get("image_512", "")
        display_name = user_info["profile"]["display_name"] or user_info["real_name"]

    ticket_message = await client.chat_postMessage(
        channel=env.slack_ticket_channel,
        text=f"New message from <@{user}>: {text}",
        blocks=[
            {
                "type": "input",
                "label": {"type": "plain_text", "text": "Tag ticket", "emoji": True},
                "element": {
                    "action_id": "tag-list",
                    "type": "multi_external_select",
                    "placeholder": {"type": "plain_text", "text": "Select tags"},
                    "min_query_length": 0,
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Submitted by <@{user}>. They have {past_tickets} past tickets. <{thread_url}|View thread>.",
                    }
                ],
            },
        ],
        username=display_name or None,
        icon_url=profile_pic or None,
        unfurl_links=True,
        unfurl_media=True,
    )

    ticket_message_ts = ticket_message["ts"]
    if not ticket_message_ts:
        logging.error(f"Ticket message has no ts: {ticket_message}")
        return

    async with env.session.post(
        "https://ai.hackclub.com/chat/completions",
        json={
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that helps organise tickets for Hack Club's support team. You're going to take in a message and give it a title. You will return no other content. Even if it's silly please summarise it. Use no more than 7 words, but as few as possible.",
                },
                {
                    "role": "user",
                    "content": f"Here is a message from a user: {text}\n\nPlease give this ticket a title.",
                },
            ]
        },
    ) as res:
        if res.status != 200:
            await send_heartbeat(
                f"Failed to get AI response for ticket creation: {res.status} - {await res.text()}"
            )
            title = "No title provided by AI."
        else:
            data = await res.json()
            title = data["choices"][0]["message"]["content"].strip()

    user_facing_message_text = (
        env.transcript.first_ticket_create.replace("(user)", display_name)
        if past_tickets == 0
        else env.transcript.ticket_create.replace("(user)", display_name)
    )
    ticket_url = f"https://hackclub.slack.com/archives/{env.slack_ticket_channel}/p{ticket_message_ts.replace('.', '')}"

    user_facing_message = await client.chat_postMessage(
        channel=event["channel"],
        text=user_facing_message_text,
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": user_facing_message_text},
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "i get it now"},
                        "style": "primary",
                        "action_id": "mark_resolved",
                        "value": f"{event['ts']}",
                    }
                ],
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"<{ticket_url}|backend> (for support team).",
                    }
                ],
            },
        ],
        thread_ts=event.get("ts"),
        unfurl_links=True,
        unfurl_media=True,
    )

    user_facing_message_ts = user_facing_message["ts"]
    if not user_facing_message_ts:
        logging.error(f"User-facing message has no ts: {user_facing_message}")
        return

    ticket = await env.db.ticket.create(
        {
            "title": title,
            "description": text,
            "msgTs": event["ts"],
            "ticketTs": ticket_message_ts,
            "openedBy": {"connect": {"id": db_user.id}},
            "userFacingMsgs": {
                "create": {
                    "channelId": event["channel"],
                    "ts": user_facing_message_ts,
                }
            },
        },
    )

    try:
        await client.reactions_add(
            channel=event["channel"], name="thinking_face", timestamp=event["ts"]
        )
    except SlackApiError as e:
        if e.response.get("error") != "message_not_found":
            raise e
        # This means the parent message has been deleted while we've been processing it
        # therefore we should unsend the bot messages and remove the ticket from the DB
        await delete_and_clean_up_ticket(ticket)

    if env.uptime_url and env.environment == "production":
        async with env.session.get(env.uptime_url) as res:
            if res.status != 200:
                await send_heartbeat(
                    f"Failed to ping uptime URL: {res.status} - {await res.text()}"
                )
            else:
                await send_heartbeat(
                    f"Successfully pinged uptime URL: {res.status} - {await res.text()}"
                )
