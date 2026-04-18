from datetime import datetime

from nephthys.database.tables import Ticket
from nephthys.database.tables import TicketStatus
from nephthys.database.tables import UserType


async def get_unanswered_tickets(since: datetime | None = None) -> list[Ticket]:
    """
    Finds tickets that have been awaiting a response from a helper for a while.

    Returns a list of tickets, in order (most stale tickets first)
    """

    query = (
        Ticket.objects()
        .where(
            (Ticket.status == TicketStatus.OPEN)
            & (Ticket.last_msg_by != UserType.HELPER)
        )
        .order_by(Ticket.last_msg_at)
    )

    if since:
        query = query.where(Ticket.last_msg_at < since)

    return await query
