import logging
from datetime import datetime
from time import perf_counter
from typing import Any
from typing import Dict

from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.macros import run_macro
from nephthys.utils.env import env
from nephthys.utils.logging import send_heartbeat
from nephthys.utils.ticket_methods import delete_and_clean_up_ticket
from prisma.enums import TicketStatus
from prisma.models import User

# Message subtypes that should be handled by on_message (messages with no subtype are always handled)
ALLOWED_SUBTYPES = ["file_share", "me_message", "thread_broadcast"]


async def handle_message_sent_to_channel(event: Dict[str, Any], client: AsyncWebClient):
    """Tell a non-helper off because they sent a thread message with the 'send to channel' box checked."""
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


async def handle_message_in_thread(event: Dict[str, Any], db_user: User | None):
    """Handle a message sent in a help thread.

    - Ignores non-helper messages.
    - If the message starts with "?", run the corresponding macro.
    - Otherwise, update the assigned helper and ticket status.
    """
    if not (db_user and db_user.helper):
        return
    ticket_message = await env.db.ticket.find_first(
        where={"msgTs": event["thread_ts"]},
        include={"openedBy": True, "tagsOnTickets": True},
    )
    if not ticket_message:
        return
    text = event.get("text", "")
    first_word = text.split()[0].lower()

    if first_word[0] == "?":
        await run_macro(
            name=first_word.lstrip("?"),
            ticket=ticket_message,
            helper=db_user,
            text=text,
            macro_ts=event["ts"],
        )
        return

    # A helper has sent a normal reply
    if ticket_message.status != TicketStatus.CLOSED:
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


async def send_ticket_message(
    event: Dict[str, Any],
    client: AsyncWebClient,
    past_tickets: int,
    display_name: str,
    profile_pic: str,
):
    """Send a "backend" message to the tickets channel with ticket details."""
    user = event.get("user", "unknown")
    text = event.get("text", "")
    thread_url = f"https://hackclub.slack.com/archives/{env.slack_help_channel}/p{event['ts'].replace('.', '')}"

    return await client.chat_postMessage(
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
        username=display_name,
        icon_url=profile_pic,
        unfurl_links=True,
        unfurl_media=True,
    )


async def handle_new_question(
    event: Dict[str, Any], client: AsyncWebClient, db_user: User | None
):
    """Handle a new support question posted in the help channel.

    Creates a ticket in the database, sends a message in the support thread
    and in the tickets channel, and generates an AI-powered ticket title.

    Args:
        event (Dict[str, Any]): The Slack event containing the new question.
        client (AsyncWebClient): Slack API client.
        db_user (User | None): The database user object, or None if user doesn't exist yet.
    """
    start_time = perf_counter()
    user = event.get("user", "unknown")
    text = event.get("text", "")
    user_info_response = await client.users_info(user=user) or {}
    slack_user_info_time = perf_counter()
    logging.debug(
        f"on_message: Slack user info fetch took {slack_user_info_time - start_time:.2f}s"
    )
    user_info = user_info_response.get("user")
    if user_info:
        profile_pic: str = user_info["profile"].get("image_512", "")
        display_name: str = (
            user_info["profile"]["display_name"] or user_info["real_name"]
        )
    else:
        profile_pic = ""
        display_name = "Explorer"

    if db_user:
        past_tickets = await env.db.ticket.count(where={"openedById": db_user.id})
    else:
        past_tickets = 0
        username = (user_info or {}).get(
            "name"
        )  # this should never actually be empty but if it is, that is a major issue

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
    db_count_time = perf_counter()
    logging.debug(
        f"on_message: Getting ticket count/updating user DB took {db_count_time - slack_user_info_time:.2f}s"
    )

    ticket_message = await send_ticket_message(
        event,
        client,
        past_tickets=past_tickets,
        display_name=display_name,
        profile_pic=profile_pic,
    )
    ticket_message_time = perf_counter()
    logging.debug(
        f"on_message: Sending ticket message took {ticket_message_time - db_count_time:.2f}s"
    )

    ticket_message_ts = ticket_message["ts"]
    if not ticket_message_ts:
        logging.error(f"Ticket message has no ts: {ticket_message}")
        return

    user_facing_message_text = (
        env.transcript.first_ticket_create.replace("(user)", display_name)
        if past_tickets == 0
        else env.transcript.ticket_create.replace("(user)", display_name)
    )
    ticket_url = f"https://hackclub.slack.com/archives/{env.slack_ticket_channel}/p{ticket_message_ts.replace('.', '')}"

    user_facing_message = await send_user_facing_message(
        event, client, text=user_facing_message_text, ticket_url=ticket_url
    )
    user_facing_message_time = perf_counter()
    logging.debug(
        f"on_message: Sending FAQ message took {user_facing_message_time - ticket_message_time:.2f}s"
    )

    title = await generate_ticket_title(text)
    ai_response_time = perf_counter()
    logging.debug(
        f"on_message: AI title generation took {ai_response_time - user_facing_message_time:.2f}s"
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
    ticket_creation_time = perf_counter()
    logging.debug(
        f"on_message: Ticket creation in DB took {ticket_creation_time - ai_response_time:.2f}s"
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


async def send_user_facing_message(
    event: Dict[str, Any], client: AsyncWebClient, text: str, ticket_url: str
):
    """Send a user-facing message in the question thread with the provided text
    and a resolve button.

    Args:
        event: The Slack event containing the original message.
        client: Slack API client.
        text: The message text to display to the user.
        ticket_url: URL to the backend ticket.

    Returns:
        The Slack API response containing the posted message.
    """
    return await client.chat_postMessage(
        channel=event["channel"],
        text=text,
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": text},
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": env.transcript.resolve_ticket_button,
                        },
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


async def on_message(event: Dict[str, Any], client: AsyncWebClient):
    """
    Handle incoming messages in Slack.
    """
    if "subtype" in event and event["subtype"] not in ALLOWED_SUBTYPES:
        return
    if "bot_id" in event:
        logging.info(f"Ignoring bot message from {event['bot_id']}")
        return

    start_time = perf_counter()

    db_user = await env.db.user.find_first(
        where={"slackId": event.get("user", "unknown")}
    )
    db_lookup_time = perf_counter()
    logging.debug(f"on_message: DB lookup took {db_lookup_time - start_time:.2f}s")

    # Messages sent in a thread with the "send to channel" checkbox checked
    if event.get("subtype") == "thread_broadcast" and not (db_user and db_user.helper):
        await handle_message_sent_to_channel(event, client)

    if event.get("thread_ts"):
        await handle_message_in_thread(event, db_user)
        return

    special_cases_time = perf_counter()
    logging.debug(
        f"on_message: Special cases took {special_cases_time - db_lookup_time:.2f}s"
    )

    await handle_new_question(event, client, db_user)

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


async def generate_ticket_title(text: str):
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
    return title
