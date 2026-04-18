import asyncio
import logging
from datetime import datetime
from datetime import timedelta
from datetime import timezone

from slack_sdk.errors import SlackApiError

from nephthys.actions.resolve import resolve
from nephthys.database.tables import Ticket
from nephthys.database.tables import TicketStatus
from nephthys.database.tables import User
from nephthys.utils.env import env
from nephthys.utils.logging import send_heartbeat


async def get_is_stale(ts: str, stale_ticket_days: int, max_retries: int = 3) -> bool:
    for attempt in range(max_retries):
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
            ) > timedelta(days=stale_ticket_days)
        except SlackApiError as e:
            if e.response["error"] == "ratelimited":
                retry_after = int(e.response.headers.get("Retry-After", 1))
                # Exponential backoff: wait longer on each retry
                wait_time = retry_after * (2**attempt)
                logging.warning(
                    f"Rate limited while fetching replies for ticket {ts}. "
                    f"Attempt {attempt + 1}/{max_retries}. Retrying after {wait_time} seconds."
                )
                await asyncio.sleep(wait_time)
                if attempt == max_retries - 1:
                    logging.error(f"Max retries exceeded for ticket {ts}")
                    return False
                continue
            elif e.response["error"] == "thread_not_found":
                logging.warning(
                    f"Thread not found for ticket {ts}. This might be a deleted thread."
                )
                await send_heartbeat(f"Thread not found for ticket {ts}.")
                maintainer_user = (
                    await User.objects()
                    .where(User.slack_id == env.slack_maintainer_id)
                    .first()
                )
                if maintainer_user:
                    await Ticket.update(
                        {
                            Ticket.status: TicketStatus.CLOSED,
                            Ticket.closed_at: datetime.now(),
                            Ticket.closed_by: maintainer_user.id,
                        }
                    ).where(Ticket.msg_ts == ts)
                else:
                    await Ticket.update(
                        {
                            Ticket.status: TicketStatus.CLOSED,
                            Ticket.closed_at: datetime.now(),
                        }
                    ).where(Ticket.msg_ts == ts)
                return False
            else:
                logging.error(
                    f"Error fetching replies for ticket {ts}: {e.response['error']}"
                )
                await send_heartbeat(
                    f"Error fetching replies for ticket {ts}: {e.response['error']}"
                )
                return False
    return False


async def close_stale_tickets():
    """
    Closes tickets that have been inactive for more than the configured number of days,
    based on the timestamp of the last message in the ticket's Slack thread.

    Configure via the STALE_TICKET_DAYS environment variable.
    This task is intended to be run periodically (e.g., hourly).
    """

    stale_ticket_days = env.stale_ticket_days
    if not stale_ticket_days:
        logging.warning("Skipping ticket auto-close (STALE_TICKET_DAYS not set)")
        return

    logging.info(f"Closing stale tickets, threshold_days={stale_ticket_days}")
    await send_heartbeat(
        f"Closing stale tickets (threshold: {stale_ticket_days} days)..."
    )

    try:
        tickets = await Ticket.objects(Ticket.opened_by, Ticket.assigned_to).where(
            Ticket.status != TicketStatus.CLOSED
        )
        stale = 0

        # Process tickets in batches to avoid overwhelming the API
        batch_size = 10
        for i in range(0, len(tickets), batch_size):
            batch = tickets[i : i + batch_size]
            logging.info(
                f"Processing stale tickets batch={i // batch_size + 1} batches={(len(tickets) + batch_size - 1) // batch_size}"
            )

            for ticket in batch:
                await asyncio.sleep(1.2)  # Rate limiting delay

                if await get_is_stale(ticket.msg_ts, stale_ticket_days):
                    stale += 1
                    resolver_user = (
                        ticket.assigned_to if ticket.assigned_to else ticket.opened_by
                    )
                    if not resolver_user:
                        logging.warning(
                            f"Skipping stale ticket {ticket.msg_ts}: no assigned or opened user"
                        )
                        continue
                    await resolve(
                        ticket.msg_ts,
                        resolver_user.slack_id,
                        env.slack_client,
                        stale=True,
                    )

            # Longer delay between batches
            if i + batch_size < len(tickets):
                await asyncio.sleep(5)

        await send_heartbeat(f"Closed {stale} stale tickets.")

        logging.info(f"Closed stale tickets. count={stale}")
    except Exception as e:
        logging.error(f"Error closing stale tickets: {e}")
        await send_heartbeat(f"Error closing stale tickets: {e}")
