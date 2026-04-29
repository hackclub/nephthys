import logging

from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.database.tables import BotMessage
from nephthys.database.tables import Ticket
from nephthys.utils.env import env


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


async def reply_to_ticket(ticket: Ticket, client: AsyncWebClient, text: str) -> None:
    """Sends a user-facing message in the help thread and records it in the database"""
    channel = env.slack_help_channel
    thread_ts = ticket.msg_ts
    msg = await client.chat_postMessage(
        channel=channel,
        text=text,
        thread_ts=thread_ts,
    )
    msg_ts = msg["ts"]
    if not msg_ts:
        logging.error(f"Bot message has no ts: {msg}")
        return
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
