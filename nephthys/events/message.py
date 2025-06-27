from typing import Any
from typing import Dict

from slack_sdk.web.async_client import AsyncWebClient

from nephthys.data.transcript import Transcript
from nephthys.macros import run_macro
from nephthys.utils.env import env
from nephthys.utils.logging import send_heartbeat

ALLOWED_SUBTYPES = ["file_share", "me_message"]


async def on_message(event: Dict[str, Any], client: AsyncWebClient):
    """
    Handle incoming messages in Slack.
    """
    if "subtype" in event and event["subtype"] not in ALLOWED_SUBTYPES:
        return

    user = event.get("user", "unknown")
    text = event.get("text", "")

    db_user = await env.db.user.find_first(where={"slackId": user})

    if event.get("thread_ts"):
        if db_user and db_user.helper:
            ticket = await env.db.ticket.find_first(
                where={"msgTs": event["thread_ts"]},
                include={"openedBy": True, "tagsOnTickets": True},
            )
            first_word = text.split()[0].lower()

            if first_word[0] == "?" and ticket:
                await run_macro(
                    name=first_word.lstrip("?"),
                    ticket=ticket,
                    helper=db_user,
                    text=text,
                    macro_ts=event["ts"],
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

    user_info = await client.users_info(user=user)
    profile_pic = None
    display_name = "Explorer"
    if user_info:
        profile_pic = user_info["user"]["profile"].get("image_512", "")
        display_name = (
            user_info["user"]["profile"]["display_name"]
            or user_info["user"]["real_name"]
        )

    ticket = await client.chat_postMessage(
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

    await env.db.ticket.create(
        {
            "title": f"New ticket from {user}",
            "description": text,
            "msgTs": event["ts"],
            "ticketTs": ticket["ts"],
            "openedBy": {"connect": {"id": db_user.id}},
        },
    )

    text = (
        Transcript.first_ticket_create.replace("(user)", display_name)
        if past_tickets == 0
        else Transcript.ticket_create.replace("(user)", display_name)
    )
    ticket_url = f"https://hackclub.slack.com/archives/{env.slack_ticket_channel}/p{ticket['ts'].replace('.', '')}"

    await client.chat_postMessage(
        channel=event["channel"],
        text=text,
        blocks=[
            {"type": "section", "text": {"type": "mrkdwn", "text": text}},
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

    await client.reactions_add(
        channel=event["channel"], name="thinking_face", timestamp=event["ts"]
    )

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
