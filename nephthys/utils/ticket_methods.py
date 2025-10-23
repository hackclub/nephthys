from slack_sdk.web.async_client import AsyncWebClient

from nephthys.utils.env import env
from prisma.models import Ticket


def reply_to_ticket(ticket: Ticket, client: AsyncWebClient, text: str) -> None:
    """Sends a user-facing message in the help thread and records it in the database"""
    channel = env.slack_help_channel
    thread_ts = ticket.msgTs
    msg = await client.chat_postMessage(
        channel=channel,
        text=text,
        thread_ts=thread_ts,
    )
    await env.db.botmessage.create(
        data={
            "msgTs": msg["ts"],
            "channelId": channel,
            "ticket": {"connect": {"id": ticket.id}},
        }
    )

