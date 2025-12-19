from datetime import datetime

from nephthys.utils.env import env
from prisma.enums import TicketStatus
from prisma.enums import UserType
from prisma.models import Ticket


async def get_unanswered_tickets(since: datetime) -> list[Ticket]:
    """
    Finds tickets that have been awaiting a response from a helper for a while.

    Returns a list of tickets, in order (most stale tickets first)
    """

    unanswered_tickets = await env.db.ticket.find_many(
        where={
            "status": TicketStatus.OPEN,
            "lastMsgAt": {"lt": since},
            "AND": [{"NOT": [{"lastMsgBy": UserType.HELPER}]}],
        },
        order={"lastMsgAt": "asc"},
    )

    return unanswered_tickets
