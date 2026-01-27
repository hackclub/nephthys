import logging
from datetime import datetime
from typing import Any
from typing import Dict

from openai import OpenAIError
from prometheus_client import Histogram
from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.events.message.send_backend_message import send_backend_message
from nephthys.macros import run_macro
from nephthys.utils.env import env
from nephthys.utils.logging import send_heartbeat
from nephthys.utils.performance import perf_timer
from nephthys.utils.slack_user import get_user_profile
from nephthys.utils.ticket_methods import delete_and_clean_up_ticket
from prisma.enums import TicketStatus
from prisma.enums import UserType
from prisma.models import User

# Message subtypes that should be handled by on_message (messages with no subtype are always handled)
ALLOWED_SUBTYPES = ["file_share", "me_message", "thread_broadcast"]

TICKET_TITLE_GENERATION_DURATION = Histogram(
    "nephthys_ticket_title_generation_duration_seconds",
    "How long it takes to generate a ticket title using AI",
)


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

    - If the message starts with "?" (and is from a helper), run the corresponding macro.
    - Otherwise, update the assigned helper, ticket status, and lastMsg fields.
    """
    ticket_message = await env.db.ticket.find_first(
        where={"msgTs": event["thread_ts"]},
        include={"openedBy": True, "tagsOnTickets": True},
    )
    if not ticket_message:
        return
    text: str = event.get("text", "")
    first_word = text.split()[0].lower() if text.strip() else ""

    if db_user and db_user.helper and first_word.startswith("?"):
        await run_macro(
            name=first_word.lstrip("?"),
            ticket=ticket_message,
            helper=db_user,
            text=text,
            macro_ts=event["ts"],
        )
        return

    # Update lastMsg fields in DB
    is_author = bool(
        ticket_message.openedBy and event["user"] == ticket_message.openedBy.slackId
    )
    is_helper = bool(db_user and db_user.helper)
    await env.db.ticket.update(
        where={"msgTs": event["thread_ts"]},
        data={
            "lastMsgAt": datetime.now(),
            "lastMsgBy": (
                UserType.AUTHOR
                if is_author
                else UserType.HELPER
                if is_helper
                else UserType.OTHER
            ),
        },
    )

    # Ensure the ticket is assigned to the helper who last sent a message
    if db_user and db_user.helper and ticket_message.status != TicketStatus.CLOSED:
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
    author_id = event.get("user", "unknown")
    text = event.get("text", "")
    async with perf_timer("Slack user info fetch"):
        author = await get_user_profile(author_id)

    if db_user:
        async with perf_timer("Getting ticket count from DB"):
            past_tickets = await env.db.ticket.count(where={"openedById": db_user.id})
    else:
        past_tickets = 0
        username = author.display_name()
        async with perf_timer("Creating user in DB"):
            db_user = await env.db.user.upsert(
                where={
                    "slackId": author_id,
                },
                data={
                    "create": {"slackId": author_id, "username": username},
                    "update": {"slackId": author_id, "username": username},
                },
            )

    async with perf_timer("Sending backend ticket message"):
        ticket_message = await send_backend_message(
            author_user_id=author_id,
            description=text,
            msg_ts=event["ts"],
            past_tickets=past_tickets,
            client=client,
            display_name=author.display_name(),
            profile_pic=author.profile_pic_512x() or "",
        )

    ticket_message_ts = ticket_message["ts"]
    if not ticket_message_ts:
        logging.error(f"Ticket message has no ts: {ticket_message}")
        return

    user_facing_message_text = (
        env.transcript.first_ticket_create.replace("(user)", author.display_name())
        if past_tickets == 0
        else env.transcript.ticket_create.replace("(user)", author.display_name())
    )
    ticket_url = f"https://hackclub.slack.com/archives/{env.slack_ticket_channel}/p{ticket_message_ts.replace('.', '')}"

    async with perf_timer("Sending user-facing FAQ message"):
        user_facing_message = await send_user_facing_message(
            event, client, text=user_facing_message_text, ticket_url=ticket_url
        )

    async with perf_timer(
        "AI ticket title generation", TICKET_TITLE_GENERATION_DURATION
    ):
        title = await generate_ticket_title(text)

    user_facing_message_ts = user_facing_message["ts"]
    if not user_facing_message_ts:
        logging.error(f"User-facing message has no ts: {user_facing_message}")
        return

    async with perf_timer("Creating ticket in DB"):
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
                    },
                    # {
                    #     "type": "button",
                    #     "text": {
                    #         "type": "plain_text",
                    #         "text": "Manage tags (helpers only)",
                    #     },
                    #     "action_id": "manage_tags_from_thread",
                    #     "value": f"{event['ts']}",
                    # },
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

    async with perf_timer("DB user lookup"):
        db_user = await env.db.user.find_first(
            where={"slackId": event.get("user", "unknown")}
        )

    # Messages sent in a thread with the "send to channel" checkbox checked
    if event.get("subtype") == "thread_broadcast" and not (db_user and db_user.helper):
        async with perf_timer("Handling message sent to channel"):
            await handle_message_sent_to_channel(event, client)

    if event.get("thread_ts"):
        await handle_message_in_thread(event, db_user)
        return

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
    if not env.ai_client:
        return "No title available from AI."

    model = "openai/gpt-oss-120b"
    try:
        response = await env.ai_client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that helps organise tickets for Hack Club's support team. You're going to take in a message and give it a title."
                        "You will return no other content. Do NOT use title case but use capital letter at start of sentence + use capital letters for terms/proper nouns."
                        "Avoid quote marks. Even if it's silly please summarise it. Use no more than 7 words, but as few as possible"
                        "When mentioning Flavortown, do *NOT* change it to 'flavor town' or 'flavour town'. Hack Club should *NOT* be changed to 'hackclub'."
                        "Hackatime, Flavortown, and Hack Club should always be capitalized correctly. Same goes for terms like VSCode, PyCharm, API, and GitHub."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Here is a message from a user: {text}\n\nPlease give this ticket a title.",
                },
            ],
        )
    except OpenAIError as e:
        await send_heartbeat(f"Failed to get AI response for ticket creation: {e}")
        return "No title provided by AI."

    if not (len(response.choices) and response.choices[0].message.content):
        await send_heartbeat(f"AI title generation is missing content: {response}")
        return "No title provided by AI."
    title = response.choices[0].message.content.strip()
    # Capitalise first letter
    title = title[0].upper() + title[1:] if len(title) > 1 else title.upper()
    return title
