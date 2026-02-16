from datetime import datetime
from datetime import timedelta

from blockkit import Header
from blockkit import Section
from blockkit import Text

from nephthys.utils.stats import calculate_daily_stats
from nephthys.utils.stats import calculate_overall_stats


async def get_leaderboard_components():
    stats = await calculate_overall_stats()
    overall_leaderboard_lines = [
        f"{i + 1}. <@{entry['user'].slackId}> - {entry['count']} closed"
        for i, entry in enumerate(stats.helpers_leaderboard)
    ]
    if not overall_leaderboard_lines:
        overall_leaderboard_str = "_No one's on the board yet!_"
    else:
        overall_leaderboard_str = "\n".join(overall_leaderboard_lines)

    now = datetime.now().astimezone()
    prev_day_start = now - timedelta(days=1)
    prev_day = await calculate_daily_stats(prev_day_start, now)

    prev_day_leaderboard_lines = [
        f"{i + 1}. <@{entry['user'].slackId}> - {entry['count']} closed"
        for i, entry in enumerate(prev_day.helpers_leaderboard)
    ]
    if not prev_day_leaderboard_lines:
        prev_day_leaderboard_str = "_No one's on the board yet!_"
    else:
        prev_day_leaderboard_str = "\n".join(prev_day_leaderboard_lines)

    avg_hang_time_str = (
        f"{stats.mean_hang_time_minutes_unresolved:.2f} minutes"
        if stats.mean_hang_time_minutes_unresolved is not None
        else "No hang time data available"
    )
    avg_prev_day_hang_time_str = (
        f"{prev_day.mean_hang_time_minutes_unresolved:.2f} minutes"
        if prev_day.mean_hang_time_minutes_unresolved is not None
        else "No hang time data available"
    )

    return [
        Section()
        .add_field(
            Text(
                f"*Total Tickets*\nTotal: {stats.tickets_total}, "
                f"Open: {stats.tickets_open}, "
                f"In Progress: {stats.tickets_in_progress}, "
                f"Closed: {stats.tickets_closed}\n"
                f"Hang time: {avg_hang_time_str}",
            )
        )
        .add_field(
            Text(
                f"*Past 24 Hours*\nTotal: {prev_day.new_tickets_total}, "
                f"Open: {prev_day.new_tickets_still_open}, "
                f"In Progress: {prev_day.assigned_today_in_progress}, "
                f"Closed: {prev_day.closed_today}, "
                f"Closed Today: {prev_day.closed_today_from_today}\n"
                f"Hang time: {avg_prev_day_hang_time_str}",
            )
        ),
        Header(":rac_lfg: leaderboard"),
        Section()
        .add_field(Text(f"*:summer25: overall*\n{overall_leaderboard_str}"))
        .add_field(Text(f"*:mc-clock: past 24 hours*\n{prev_day_leaderboard_str}")),
    ]
