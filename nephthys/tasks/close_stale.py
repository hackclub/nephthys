import asyncio
import logging
from datetime import datetime
from datetime import timedelta
from datetime import timezone

from slack_sdk.errors import SlackApiError

from nephthys.actions.resolve import resolve
from nephthys.utils.env import env
from nephthys.utils.logging import send_heartbeat
from prisma.enums import TicketStatus


async def get_is_stale(ts: str) -> bool:
    try:
        replies = await env.slack_client.conversations_replies(
            channel=env.slack_help_channel, ts=ts, limit=1000
        )
        last_reply = (
            replies.get("messages", [])[-1] if replies.get("messages") else None
        )
        if not last_reply:
            logging.error("No replies found - this should never happen")
            await send_heartbeat(f"No replies found for ticket {ts}")
            return False
        return (
            datetime.now(tz=timezone.utc)
            - datetime.fromtimestamp(float(last_reply["ts"]), tz=timezone.utc)
        ) > timedelta(days=3)
    except SlackApiError as e:
        if e.response["error"] == "ratelimited":
            retry_after = int(e.response.headers.get("Retry-After", 1))
            logging.warning(
                f"Rate limited while fetching replies for ticket {ts}. Retrying after {retry_after} seconds."
            )
            await asyncio.sleep(retry_after)
            return await get_is_stale(ts)
        else:
            logging.error(
                f"Error fetching replies for ticket {ts}: {e.response['error']}"
            )
            await send_heartbeat(
                f"Error fetching replies for ticket {ts}: {e.response['error']}"
            )
            return False


async def close_stale_tickets():
    """
    Closes tickets that have been open for more than 3 days.
    This task is intended to be run periodically.
    """

    logging.info("Closing stale tickets...")
    await send_heartbeat("Closing stale tickets...")

    try:
        tickets = await env.db.ticket.find_many(
            where={"NOT": [{"status": TicketStatus.CLOSED}]},
            include={
                "openedBy": True,
            },
        )
        stale_tickets = [
            ticket for ticket in tickets if await get_is_stale(ticket.msgTs)
        ]

        for ticket in stale_tickets:
            await resolve(
                ticket.msgTs,
                ticket.openedBy.slackId,  # type: ignore (this is valid - see include above)
                env.slack_client,
                stale=True,
            )

        await send_heartbeat(f"Closed {len(stale_tickets)} stale tickets.")

        logging.info(f"Closed {len(stale_tickets)} stale tickets.")
    except Exception as e:
        logging.error(f"Error closing stale tickets: {e}")
        await send_heartbeat(f"Error closing stale tickets: {e}")
