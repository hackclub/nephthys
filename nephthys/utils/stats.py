from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict

from nephthys.utils.env import env
from prisma.enums import TicketStatus
from prisma.models import Ticket
from prisma.models import User


class LeaderboardEntry(TypedDict):
    user: User
    count: int


@dataclass
class OverallStatsResult:
    tickets_total: int
    tickets_open: int
    tickets_closed: int
    tickets_in_progress: int
    helpers_leaderboard: list[LeaderboardEntry]
    avg_hang_time_minutes: float | None


def calculate_avg_hang_time(tickets: list[Ticket]) -> float | None:
    hang_times = []
    for tkt in tickets:
        if tkt.status == TicketStatus.CLOSED:
            continue
        if not tkt.assignedAt:
            continue
        hang_times.append((tkt.assignedAt - tkt.createdAt).total_seconds() / 60)
    return sum(hang_times) / len(hang_times) if hang_times else None


async def calculate_overall_stats() -> OverallStatsResult:
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
    helpers_closed_tickets_counts: list[LeaderboardEntry] = [
        {"user": user, "count": len(user.closedTickets)}
        for user in users_with_closed_tickets
        if user.closedTickets
    ]
    helpers_leaderboard = sorted(
        helpers_closed_tickets_counts,
        key=lambda entry: entry["count"],
        reverse=True,
    )

    return OverallStatsResult(
        tickets_total=total,
        tickets_open=total_open,
        tickets_closed=total_closed,
        tickets_in_progress=total_in_progress,
        helpers_leaderboard=helpers_leaderboard,
        avg_hang_time_minutes=calculate_avg_hang_time(tickets),
    )


@dataclass
class DailyStatsResult:
    new_tickets_total: int
    new_tickets_now_closed: int
    new_tickets_still_open: int
    new_tickets_in_progress: int
    closed_today: int
    closed_today_from_today: int
    assigned_today_in_progress: int
    helpers_leaderboard: list[LeaderboardEntry]
    avg_hang_time_minutes: float | None


async def calculate_daily_stats(
    start_time: datetime, end_time: datetime
) -> DailyStatsResult:
    tickets = await env.db.ticket.find_many() or []
    users_with_closed_tickets = await env.db.user.find_many(
        include={"closedTickets": True},
        where={"helper": True, "closedTickets": {"some": {}}},
    )

    new_tickets_total = len(
        [t for t in tickets if start_time <= t.createdAt < end_time]
    )
    new_tickets_now_closed = len(
        [
            t
            for t in tickets
            if t.status == TicketStatus.CLOSED
            and t.closedAt
            and start_time <= t.closedAt < end_time
            and start_time <= t.createdAt < end_time
        ]
    )
    new_tickets_still_open = len(
        [
            t
            for t in tickets
            if start_time <= t.createdAt < end_time and t.status == TicketStatus.OPEN
        ]
    )
    new_tickets_in_progress = len(
        [
            t
            for t in tickets
            if t.assignedAt
            and start_time <= t.assignedAt < end_time
            and t.status == TicketStatus.IN_PROGRESS
        ]
    )
    tickets_closed_today = [
        t
        for t in tickets
        if t.status == TicketStatus.CLOSED
        and t.closedAt
        and start_time <= t.closedAt < end_time
    ]
    closed_today = len(tickets_closed_today)
    closed_today_from_today = len(
        [t for t in tickets_closed_today if start_time <= t.createdAt < end_time]
    )
    assigned_today_in_progress = len(
        [
            t
            for t in tickets
            if t.assignedAt
            and start_time <= t.assignedAt < end_time
            and t.status == TicketStatus.IN_PROGRESS
        ]
    )

    leaderboard_data = []
    for user in users_with_closed_tickets:
        daily_closed_count = sum(
            1
            for ticket in (user.closedTickets or [])
            if ticket.closedAt and start_time <= ticket.closedAt < end_time
        )
        if daily_closed_count > 0:
            leaderboard_data.append({"user": user, "count": daily_closed_count})
    helpers_leaderboard = sorted(
        leaderboard_data,
        key=lambda data: data["count"],
        reverse=True,
    )

    hang_time = calculate_avg_hang_time(
        [t for t in tickets if start_time <= t.createdAt < end_time]
    )

    return DailyStatsResult(
        closed_today=closed_today,
        closed_today_from_today=closed_today_from_today,
        assigned_today_in_progress=assigned_today_in_progress,
        helpers_leaderboard=helpers_leaderboard,
        new_tickets_total=new_tickets_total,
        new_tickets_now_closed=new_tickets_now_closed,
        new_tickets_in_progress=new_tickets_in_progress,
        new_tickets_still_open=new_tickets_still_open,
        avg_hang_time_minutes=hang_time,
    )
