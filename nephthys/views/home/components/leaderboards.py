from datetime import datetime
from datetime import timedelta

import pytz

from nephthys.utils.env import env
from prisma.enums import TicketStatus


async def get_leaderboard_view(tz=None):
    tickets = await env.db.ticket.find_many() or []
    users_with_closed_tickets = await env.db.user.find_many(
        include={"closedTickets": True, "assignedTickets": True}, where={"helper": True}
    )
    total_open = len([t for t in tickets if t.status == TicketStatus.OPEN])
    total_in_progress = len(
        [t for t in tickets if t.status == TicketStatus.IN_PROGRESS]
    )
    total_closed = len([t for t in tickets if t.status == TicketStatus.CLOSED])
    total = len(tickets)
    sorted_users_overall = sorted(
        users_with_closed_tickets,
        key=lambda user: len(user.closedTickets or []),
        reverse=True,
    )
    overall_leaderboard_lines = [
        f"{i + 1}. <@{user.slackId}> - {len(user.closedTickets or [])} closed, {len([t for t in user.assignedTickets or [] if t.status != TicketStatus.CLOSED])} assigned"
        for i, user in enumerate(sorted_users_overall)
    ]
    if not overall_leaderboard_lines:
        overall_leaderboard_str = "_No one's on the board yet!_"
    else:
        overall_leaderboard_str = "\n".join(overall_leaderboard_lines)

    # Use UTC as fallback if no timezone provided
    if tz is None:
        tz = pytz.UTC

    now = datetime.now(tz)
    prev_day_start = now - timedelta(days=1)

    prev_day_total = len(
        [t for t in tickets if prev_day_start < t.createdAt.replace(tzinfo=tz) < now]
    )
    prev_day_only_closed = len(
        [
            t
            for t in tickets
            if t.status == TicketStatus.CLOSED
            and t.closedAt
            and prev_day_start < t.closedAt.replace(tzinfo=tz) < now
            and prev_day_start < t.createdAt.replace(tzinfo=tz) < now
        ]
    )
    prev_day_open = len(
        [
            t
            for t in tickets
            if prev_day_start < t.createdAt.replace(tzinfo=tz) < now
            and t.status == TicketStatus.OPEN
        ]
    )
    prev_day_in_progress = len(
        [
            t
            for t in tickets
            if t.assignedAt
            and prev_day_start < t.assignedAt.replace(tzinfo=tz) < now
            and t.status == TicketStatus.IN_PROGRESS
        ]
    )
    prev_day_closed = len(
        [
            t
            for t in tickets
            if t.status == TicketStatus.CLOSED
            and t.closedAt
            and prev_day_start < t.closedAt.replace(tzinfo=tz) < now
        ]
    )
    prev_day_leaderboard_lines = [
        f"{i + 1}. <@{user.slackId}> - {len([t for t in user.closedTickets or [] if prev_day_start < t.closedAt.replace(tzinfo=tz) < now])} closed, {len([t for t in user.assignedTickets or [] if prev_day_start < t.createdAt.replace(tzinfo=tz) < now and t.status != TicketStatus.CLOSED])} assigned"
        for i, user in enumerate(
            sorted(
                users_with_closed_tickets,
                key=lambda user: len(
                    [
                        t
                        for t in user.closedTickets or []
                        if prev_day_start < t.closedAt.replace(tzinfo=tz) < now
                    ]
                ),
                reverse=True,
            )
        )
    ]
    if not prev_day_leaderboard_lines:
        prev_day_leaderboard_str = "_No one's on the board yet!_"
    else:
        prev_day_leaderboard_str = "\n".join(prev_day_leaderboard_lines)

    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": ":rac_lfg: leaderboard",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*:summer25: overall*\n{overall_leaderboard_str}",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*:mc-clock: past 24 hours*\n{prev_day_leaderboard_str}",
                },
            ],
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Total Tickets*\nTotal: {total}, Open: {total_open}, In Progress: {total_in_progress}, Closed: {total_closed}",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Past 24 Hours*\nTotal: {prev_day_total}, Open: {prev_day_open}, In Progress: {prev_day_in_progress}, Closed: {prev_day_closed}, Closed Today: {prev_day_only_closed}",
                },
            ],
        },
    ]
