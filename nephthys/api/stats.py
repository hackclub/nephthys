from datetime import datetime
from datetime import timedelta
from datetime import timezone

from starlette.requests import Request
from starlette.responses import JSONResponse

from nephthys.utils.env import env
from prisma.enums import TicketStatus


async def stats(req: Request):
    tickets = await env.db.ticket.find_many() or []
    total_open = len([t for t in tickets if t.status == TicketStatus.OPEN])
    total_in_progress = len(
        [t for t in tickets if t.status == TicketStatus.IN_PROGRESS]
    )
    total_closed = len([t for t in tickets if t.status == TicketStatus.CLOSED])
    total = len(tickets)

    non_open_tickets = [t for t in tickets if t.status != TicketStatus.CLOSED]
    hang_times = []
    for ticket in non_open_tickets:
        if ticket.assignedAt:
            hang_time = (
                ticket.assignedAt - ticket.createdAt
            ).total_seconds() / 60  # Convert to minutes
            hang_times.append(hang_time)
    if hang_times:
        avg_hang_time_minutes = sum(hang_times) / len(hang_times)
    else:
        avg_hang_time_minutes = None

    users_with_closed_tickets = await env.db.user.find_many(
        include={"closedTickets": {}}, where={"helper": True}
    )

    # Sort the users by the count of their closed tickets in descending order
    sorted_users = sorted(
        users_with_closed_tickets,
        key=lambda user: len(user.closedTickets or []),
        reverse=True,
    )

    total_top_3_users = sorted_users[:3]

    prev_day_tickets = await env.db.ticket.find_many(
        where={"createdAt": {"gte": datetime.now() - timedelta(days=1)}}
    )
    prev_day_total = len(prev_day_tickets)
    prev_day_open = len([t for t in prev_day_tickets if t.status == TicketStatus.OPEN])
    prev_day_in_progress = len(
        [t for t in prev_day_tickets if t.status == TicketStatus.IN_PROGRESS]
    )
    prev_day_closed = len(
        [t for t in prev_day_tickets if t.status == TicketStatus.CLOSED]
    )
    prev_day_total = len(prev_day_tickets)

    prev_day_non_open_tickets = [
        t for t in prev_day_tickets if t.status != TicketStatus.CLOSED
    ]
    prev_day_hang_times = []
    for ticket in prev_day_non_open_tickets:
        if ticket.assignedAt:
            hang_time = (
                ticket.assignedAt - ticket.createdAt
            ).total_seconds() / 60  # Convert to minutes
            prev_day_hang_times.append(hang_time)
    if prev_day_hang_times:
        avg_prev_day_hang_time_minutes = sum(prev_day_hang_times) / len(
            prev_day_hang_times
        )
    else:
        avg_prev_day_hang_time_minutes = None

    one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)
    prev_24_resolvers = [
        user
        for user in users_with_closed_tickets
        if user.closedTickets
        and any(
            ticket.closedAt and ticket.closedAt >= one_day_ago
            for ticket in user.closedTickets
        )
    ]

    prev_day_top_3_users = sorted(
        prev_24_resolvers,
        key=lambda user: len(
            [
                t
                for t in (user.closedTickets or [])
                if t.closedAt and t.closedAt >= one_day_ago
            ]
        ),
        reverse=True,
    )[:3]

    return JSONResponse(
        {
            "total_tickets": total,
            "total_open": total_open,
            "total_in_progress": total_in_progress,
            "total_closed": total_closed,
            "total_top_3_users_with_closed_tickets": [
                {
                    "user_id": user.id,
                    "slack_id": user.slackId,
                    "closed_ticket_count": len(user.closedTickets or []),
                }
                for user in total_top_3_users
            ],
            "average_hang_time_minutes": avg_hang_time_minutes,
            "prev_day_total": prev_day_total,
            "prev_day_open": prev_day_open,
            "prev_day_in_progress": prev_day_in_progress,
            "prev_day_closed": prev_day_closed,
            "prev_day_top_3_users_with_closed_tickets": [
                {
                    "user_id": user.id,
                    "slack_id": user.slackId,
                    "closed_ticket_count": len(
                        [
                            t
                            for t in (user.closedTickets or [])
                            if t.closedAt and t.closedAt >= one_day_ago
                        ]
                    ),
                }
                for user in prev_day_top_3_users
            ],
            "prev_day_average_hang_time_minutes": avg_prev_day_hang_time_minutes,
        }
    )
