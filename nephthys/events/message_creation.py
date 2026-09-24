import logging
from datetime import datetime
from typing import Any

from httpx import HTTPStatusError
from openai import OpenAIError
from prometheus_client import Histogram
from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.database.enums import TicketStatus
from nephthys.database.enums import UserType
from nephthys.database.tables import BotMessage
from nephthys.database.tables import CategoryTag
from nephthys.database.tables import Ticket
from nephthys.database.tables import User
from nephthys.events.message.send_backend_message import backend_message_blocks
from nephthys.events.message.send_backend_message import backend_message_fallback_text
from nephthys.events.message.send_backend_message import send_backend_message
from nephthys.macros import run_macro
from nephthys.utils.ai import ai_client
from nephthys.utils.ai import OpenRouterClient
from nephthys.utils.env import env
from nephthys.utils.logging import send_heartbeat
from nephthys.utils.performance import perf_timer
from nephthys.utils.slack_user import get_user_profile
from nephthys.utils.ticket_methods import delete_and_clean_up_ticket
from nephthys.utils.ticket_methods import ThreadGoneError

# Message subtypes that should be handled by on_message (messages with no subtype are always handled)
ALLOWED_SUBTYPES = ["file_share", "me_message", "thread_broadcast"]

TICKET_TITLE_GENERATION_DURATION = Histogram(
    "nephthys_ticket_title_generation_duration_seconds",
    "How long it takes to generate a ticket title using AI",
)


TICKET_CATEGORY_GENERATION_DURATION = Histogram(
    "nephthys_ticket_category_generation_duration_seconds",
    "How long it takes to generate a category tag using AI",
)


async def handle_message_sent_to_channel(event: dict[str, Any], client: AsyncWebClient):
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


async def handle_message_in_thread(event: dict[str, Any], db_user: User | None):
    """Handle a message sent in a help thread.

    - If the message starts with "?" (and is from a helper), run the corresponding macro.
    - Otherwise, update the assigned helper, ticket status, and lastMsg fields.
    """
    ticket_message = (
        await Ticket.objects(Ticket.opened_by)
        .where(Ticket.msg_ts == event["thread_ts"])
        .first()
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
        ticket_message.opened_by and event["user"] == ticket_message.opened_by.slack_id
    )
    is_helper = bool(db_user and db_user.helper)
    await Ticket.update(
        {
            Ticket.last_msg_at: datetime.now(),
            Ticket.last_msg_by: (
                UserType.AUTHOR
                if is_author
                else UserType.HELPER
                if is_helper
                else UserType.OTHER
            ),
        }
    ).where(Ticket.msg_ts == event["thread_ts"])

    # Ensure the ticket is assigned to the helper who last sent a message
    if db_user and db_user.helper and ticket_message.status != TicketStatus.CLOSED:
        logging.info(
            f"Assigning ticket ticket_id={ticket_message.id} to helper user_id={db_user.id}"
        )
        await Ticket.update(
            {
                Ticket.assigned_to: db_user.id,
                Ticket.status: TicketStatus.IN_PROGRESS,
                Ticket.assigned_at: (
                    datetime.now()
                    if not ticket_message.assigned_at
                    else ticket_message.assigned_at
                ),
            }
        ).where(Ticket.msg_ts == event["thread_ts"])


async def handle_new_question(
    event: dict[str, Any], client: AsyncWebClient, db_user: User | None
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
            past_tickets = await Ticket.count().where(Ticket.opened_by == db_user.id)
        db_user_id = db_user.id
    else:
        past_tickets = 0
        username = author.username()
        async with perf_timer("Creating user in DB"):
            updated_records = (
                await User.insert(User(slack_id=author_id, username=username))
                .on_conflict(
                    target=User.slack_id,
                    action="DO UPDATE",
                    values=[User.username],
                )
                .returning(User.id)
            )
            if not updated_records or not updated_records[0].get("id"):
                raise ValueError(
                    f"Failed to upsert user in DB for slack_id={author_id}"
                )
            db_user_id = updated_records[0]["id"]

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

    try:
        async with perf_timer("Sending user-facing FAQ message"):
            user_facing_message = await send_user_facing_message(
                event, client, text=user_facing_message_text, ticket_url=ticket_url
            )
    except ThreadGoneError:
        logging.warning(
            f"Cancelling ticket-creation actions because thread appears to be gone thread_ts={event['ts']}"
        )
        return

    async with perf_timer(
        "AI ticket title generation", TICKET_TITLE_GENERATION_DURATION
    ):
        title = await generate_ticket_title(text)

    async with perf_timer(
        "AI category tag generation", TICKET_CATEGORY_GENERATION_DURATION
    ):
        category_tag = await generate_category_tag(text)

    if category_tag:
        blocks = await backend_message_blocks(
            author_user_id=author_id,
            msg_ts=event["ts"],
            past_tickets=past_tickets,
            current_category_tag_id=category_tag.id,
        )

        await client.chat_update(
            channel=env.slack_ticket_channel,
            ts=ticket_message_ts,
            text=backend_message_fallback_text(author_id, text),
            blocks=blocks,
        )

    user_facing_message_ts = user_facing_message["ts"]
    if not user_facing_message_ts:
        logging.error(f"User-facing message has no ts: {user_facing_message}")
        return

    async with perf_timer("Creating ticket in DB"):
        ticket = Ticket(
            title=title,
            description=text,
            status=TicketStatus.OPEN,
            msg_ts=event["ts"],
            ticket_ts=ticket_message_ts,
            opened_by=db_user_id,
            assigned_at=None,
            closed_at=None,
            reopened_at=None,
        )
        if category_tag:
            ticket.category_tag = category_tag
        await ticket.save()

        bot_msg = BotMessage(
            channel_id=event["channel"],
            ts=user_facing_message_ts,
            ticket=ticket.id,
        )
        await bot_msg.save()

    try:
        await client.reactions_add(
            channel=event["channel"], name="thinking_face", timestamp=event["ts"]
        )
    except SlackApiError as e:
        if e.response.get("error") != "message_not_found":
            raise e
        # This means the parent message has been deleted while we've been processing it
        # therefore we should unsend the bot messages and remove the ticket from the DB
        logging.warning(
            f"Top-level message for thread_ts={event['ts']} has been deleted. Cleaning up and deleting ticket_id={ticket.id}"
        )
        await delete_and_clean_up_ticket(ticket)


async def send_user_facing_message(
    event: dict[str, Any], client: AsyncWebClient, text: str, ticket_url: str
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
    response = await client.chat_postMessage(
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
    msg: dict = response["message"]  # type: ignore (assuming it exists)
    msg_ts = msg.get("ts")
    if not msg_ts:
        raise ValueError(f"User-facing message has no ts: {msg}")
    if not msg.get("thread_ts"):
        logging.warning(
            f"User-facing message was sent outside of thread. Attempted to send to thread_ts={event['ts']}. Unsending."
        )
        await client.chat_delete(channel=event["channel"], ts=msg_ts)
        raise ThreadGoneError()
    return msg


async def on_message(event: dict[str, Any], client: AsyncWebClient):
    """
    Handle incoming messages in Slack.
    """
    if "subtype" in event and event["subtype"] not in ALLOWED_SUBTYPES:
        return
    if "bot_id" in event:
        logging.info(f"Ignoring bot message from {event['bot_id']}")
        return

    async with perf_timer("DB user lookup"):
        db_user = (
            await User.objects()
            .where(User.slack_id == event.get("user", "unknown"))
            .first()
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


async def generate_ticket_title(text: str) -> str | None:
    if not ai_client:
        return None

    model = env.ai_title_model
    try:
        response = await ai_client.chat.completions.create(
            model=model,
            reasoning_effort="low",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that helps organise tickets for Hack Club's support team. You're going to take in a message and give it a title. "
                        "The title will be used for internal dashboards, short ticket lists, and other similar places. "
                        "You will return no other content. Use proper sentence case, not title case. Avoid quote marks."
                        "Even if it's silly please summarise it. Be aware, you cannot see uploaded attachments. "
                        "Use no more than 7 words, but as few as possible. "
                        "Some internal terms you should spell/capitalise correctly: Hack Club, Hackatime, Stardance. "
                        "Also correctly capitalise terms like VSCode, PyCharm, API, and GitHub."
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
        return None

    if not (len(response.choices) and response.choices[0].message.content):
        await send_heartbeat(f"AI title generation is missing content: {response}")
        return None
    title = response.choices[0].message.content.strip()
    # Capitalise first letter
    title = title[0].upper() + title[1:] if len(title) > 1 else title.upper()
    return title


async def generate_category_tag(text: str) -> CategoryTag | None:
    category_tags = await CategoryTag.objects()
    if not category_tags or not ai_client:
        return None
    if not isinstance(ai_client, OpenRouterClient):
        logging.warning(
            "Category tags are configured, but an OpenRouter API client is not available. Skipping AI category tagging."
        )
        return None

    model = env.ai_category_model

    try:
        response = await ai_client.decisions(
            model=model,
            state={
                "ticket": {
                    "message_content": text,
                }
            },
            questions={
                "category": {
                    "type": "choice",
                    "instructions": "Which internal tracking category should this ticket be labeled as?",
                    "criteria": {tag.name: tag.description for tag in category_tags},
                }
            },
        )
    except HTTPStatusError as e:
        logging.error(f'Failed to categorise ticket text="{text}" error="{e}"')
        await send_heartbeat(f"Failed to get AI response for tag generation: {e}")
        return None

    category_answer = response["answers"].get("category")
    if not category_answer or category_answer["type"] != "choice":
        logging.error(
            f'AI response is missing category answer for text="{text}" response="{response}"'
        )
        return None
    chosen_category = category_answer["choice"]
    category_tag = next(
        (tag for tag in category_tags if tag.name == chosen_category), None
    )
    if not category_tag:
        logging.error(f'AI chose invalid category tag name: "{chosen_category}"')
        return None

    tokens = response.get("usage", {}).get("input_tokens", "?")
    logging.info(
        f"Successfully generated category tag category={category_tag.slug} confidence={category_answer.get('confidence', '?')} tokens={tokens}"
    )

    return category_tag
