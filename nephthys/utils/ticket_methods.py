import logging

from blockkit.core import MessageBlock
from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.database.tables import BotMessage
from nephthys.database.tables import Ticket
from nephthys.utils.env import env


class ThreadGoneError(Exception):
    """Raise when we try to end a message to that thread, but the thread no longer exists

    This can happen when the top-level message is deleted.
    """


async def delete_message(channel_id: str, message_ts: str):
    """Deletes a Slack message, or does nothing if the message doesn't exist"""
    try:
        await env.slack_client.chat_delete(channel=channel_id, ts=message_ts)
    except SlackApiError as e:
        if e.response.get("error") != "message_not_found":
            raise e
        logging.warning(
            f"Tried to delete message {message_ts} in channel {channel_id} but it doesn't exist (already deleted?)"
        )


async def reply_to_ticket(
    ticket: Ticket,
    client: AsyncWebClient,
    text: str,
    blocks: list[MessageBlock] | None = None,
) -> None:
    """Sends a user-facing message in the help thread and records it in the database"""
    channel = env.slack_help_channel
    thread_ts = ticket.msg_ts
    response = await client.chat_postMessage(
        channel=channel,
        text=text,
        thread_ts=thread_ts,
        blocks=[block.build() for block in blocks] if blocks else None,
    )
    msg: dict = response["message"]  # type: ignore (assuming message exists)
    msg_ts = msg.get("ts")
    msg_thread_ts = msg.get("thread_ts")
    if not msg_ts:
        raise ValueError(f"Bot message has no ts: {msg}")
    if not msg_thread_ts:
        # The thread probably got deleted while we were processing the event
        logging.warning(
            f"Reply to ticket was sent outside of thread. Attempted to send to thread_ts={thread_ts} for ticket_id={ticket.id}. Unsending."
        )
        await client.chat_delete(channel=channel, ts=msg_ts)
        raise ThreadGoneError()
    bot_msg = BotMessage(ts=msg_ts, channel_id=channel, ticket=ticket.id)
    await bot_msg.save()


async def delete_bot_replies(ticket_ref: int):
    """Deletes all bot replies sent in a ticket thread"""
    ticket = await Ticket.objects().where(Ticket.id == ticket_ref).first()
    if not ticket:
        raise ValueError(f"Ticket with ID {ticket_ref} does not exist")
    bot_msgs = await BotMessage.objects().where(BotMessage.ticket == ticket_ref)
    if not bot_msgs:
        raise ValueError(f"userFacingMsgs is not present on Ticket ID {ticket_ref}")
    for bot_msg in bot_msgs:
        await delete_message(bot_msg.channel_id, bot_msg.ts)
        await bot_msg.remove()


async def delete_and_clean_up_ticket(ticket: Ticket):
    """Removes a ticket from the DB and deletes all Slack messages associated with it"""
    await delete_bot_replies(ticket.id)
    # Delete the backend message in the "tickets" channel
    await delete_message(env.slack_ticket_channel, ticket.ticket_ts)
    # TODO deal with DMs to tag subscribers?
    await Ticket.delete().where(Ticket.id == ticket.id)


def get_question_message_link(ticket: Ticket) -> str:
    """Get the Slack message link to the original help message for the provided ticket"""
    return f"https://hackclub.slack.com/archives/{env.slack_help_channel}/p{ticket.msg_ts.replace('.', '')}"


def get_backend_message_link(ticket: Ticket) -> str:
    """Get the Slack message link to the backend ticket message for the provided ticket"""
    return f"https://hackclub.slack.com/archives/{env.slack_ticket_channel}/p{ticket.ticket_ts.replace('.', '')}"
