import logging

from slack_sdk.web.async_client import AsyncWebClient

from nephthys.utils.delete_thread import add_message_to_delete_queue
from nephthys.utils.env import env
from prisma.models import Ticket


async def reply_to_ticket(ticket: Ticket, client: AsyncWebClient, text: str) -> None:
    """Sends a user-facing message in the help thread and records it in the database"""
    channel = env.slack_help_channel
    thread_ts = ticket.msgTs
    msg = await client.chat_postMessage(
        channel=channel,
        text=text,
        thread_ts=thread_ts,
    )
    msg_ts = msg["ts"]
    if not msg_ts:
        logging.error(f"Bot message has no ts: {msg}")
        return
    await env.db.botmessage.create(
        data={
            "ts": msg_ts,
            "channelId": channel,
            "ticket": {"connect": {"id": ticket.id}},
        }
    )


async def delete_replies_to_ticket(ticket: Ticket):
    """Deletes all bot replies sent in a ticket thread"""
    for bot_msg in ticket.userFacingMsgs or []:
        await add_message_to_delete_queue(bot_msg.channelId, bot_msg.ts)
        await env.db.botmessage.delete(where={"id": bot_msg.id})


async def delete_and_clean_up_ticket(ticket: Ticket):
    """Removes a ticket from the DB and deletes all Slack messages associated with it"""
    await delete_replies_to_ticket(ticket)
    await add_message_to_delete_queue(env.slack_help_channel, ticket.ticketTs)
    # TODO deal with DMs to tag subscribers?
    await env.db.ticket.delete(where={"id": ticket.id})
