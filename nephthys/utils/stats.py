from dataclasses import dataclass
from datetime import datetime
from statistics import fmean
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
    mean_resolution_time_minutes: float | None

    def as_dict(self) -> dict:
        # Warning: Changing these keys will break the stats API
        return {
            "tickets_total": self.tickets_total,
            "tickets_open": self.tickets_open,
            "tickets_closed": self.tickets_closed,
            "tickets_in_progress": self.tickets_in_progress,
            "helpers_leaderboard": [
                {
                    "id": entry["user"].id,
                    "slack_id": entry["user"].slackId,
                    "count": entry["count"],
                }
                for entry in self.helpers_leaderboard
            ],
            "avg_hang_time_minutes": self.avg_hang_time_minutes,
            "mean_resolution_time_minutes": self.mean_resolution_time_minutes,
        }


def calculate_hang_times(
    tickets: list[Ticket], include_closed_tickets: bool
) -> list[float]:
    hang_times = []
    for tkt in tickets:
        if not include_closed_tickets and tkt.status == TicketStatus.CLOSED:
            continue
        if not tkt.assignedAt:
            continue
        hang_times.append((tkt.assignedAt - tkt.createdAt).total_seconds() / 60)
    return hang_times


def calculate_resolution_times(tickets: list[Ticket]) -> list[float]:
    resolution_times = []
    for tkt in tickets:
        if not tkt.closedAt:
            continue
        resolution_times.append((tkt.closedAt - tkt.createdAt).total_seconds() / 60)
    return resolution_times


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

    hang_times = calculate_hang_times(tickets, include_closed_tickets=False)
    resolution_times = calculate_resolution_times(tickets)

    return OverallStatsResult(
        tickets_total=total,
        tickets_open=total_open,
        tickets_closed=total_closed,
        tickets_in_progress=total_in_progress,
        helpers_leaderboard=helpers_leaderboard,
        avg_hang_time_minutes=fmean(hang_times) if hang_times else None,
        mean_resolution_time_minutes=fmean(resolution_times)
        if resolution_times
        else None,
    )


@dataclass
class DailyStatsResult:
    """Processed statistics for a time interval
    (usually 24h but doesn't have to be)"""

    new_tickets_total: int
    new_tickets_now_closed: int
    new_tickets_still_open: int
    new_tickets_in_progress: int
    closed_today: int
    closed_today_from_today: int
    assigned_today_in_progress: int
    helpers_leaderboard: list[LeaderboardEntry]
    # Mean time to response for tickets created today and currently in-progress
    avg_hang_time_current_minutes: float | None
    # Mean time to response for all tickets created today
    avg_hang_time_all_minutes: float | None
    # Mean time to resolution for tickets created today
    mean_resolution_time_minutes: float | None

    def as_dict(self) -> dict:
        # Warning: Changing these keys will break the stats API
        return {
            "new_tickets_total": self.new_tickets_total,
            "new_tickets_now_closed": self.new_tickets_now_closed,
            "new_tickets_still_open": self.new_tickets_still_open,
            "new_tickets_in_progress": self.new_tickets_in_progress,
            "closed_today": self.closed_today,
            "closed_today_from_today": self.closed_today_from_today,
            "assigned_today_in_progress": self.assigned_today_in_progress,
            "helpers_leaderboard": [
                {
                    "id": entry["user"].id,
                    "slack_id": entry["user"].slackId,
                    "count": entry["count"],
                }
                for entry in self.helpers_leaderboard
            ],
            "avg_hang_time_live_minutes": self.avg_hang_time_current_minutes,
            "avg_hang_time_minutes": self.avg_hang_time_all_minutes,
            "mean_resolution_time_minutes": self.mean_resolution_time_minutes,
        }


async def calculate_daily_stats(
    start_time: datetime, end_time: datetime
) -> DailyStatsResult:
    tickets = await env.db.ticket.find_many() or []
    tickets_created_today = [t for t in tickets if start_time <= t.createdAt < end_time]
    users_with_closed_tickets = await env.db.user.find_many(
        include={"closedTickets": True},
        where={"helper": True, "closedTickets": {"some": {}}},
    )

    new_tickets_total = len(tickets_created_today)
    new_tickets_now_closed = len(
        [
            t
            for t in tickets_created_today
            if t.status == TicketStatus.CLOSED
            and t.closedAt
            and start_time <= t.closedAt < end_time
        ]
    )
    new_tickets_still_open = len(
        [t for t in tickets_created_today if t.status == TicketStatus.OPEN]
    )
    new_tickets_in_progress = len(
        [t for t in tickets_created_today if t.status == TicketStatus.IN_PROGRESS]
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

    hang_times_current = calculate_hang_times(
        tickets_created_today, include_closed_tickets=False
    )
    hang_times_all = calculate_hang_times(
        tickets_created_today, include_closed_tickets=True
    )
    resolution_times = calculate_resolution_times(tickets_created_today)
    hang_time_current = fmean(hang_times_current) if hang_times_current else None
    hang_time_all = fmean(hang_times_all) if hang_times_all else None
    resolution_time = fmean(resolution_times) if resolution_times else None

    return DailyStatsResult(
        closed_today=closed_today,
        closed_today_from_today=closed_today_from_today,
        assigned_today_in_progress=assigned_today_in_progress,
        helpers_leaderboard=helpers_leaderboard,
        new_tickets_total=new_tickets_total,
        new_tickets_now_closed=new_tickets_now_closed,
        new_tickets_in_progress=new_tickets_in_progress,
        new_tickets_still_open=new_tickets_still_open,
        avg_hang_time_current_minutes=hang_time_current,
        avg_hang_time_all_minutes=hang_time_all,
        mean_resolution_time_minutes=resolution_time,
    )
