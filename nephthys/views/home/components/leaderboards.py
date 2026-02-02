from datetime import datetime
from datetime import timedelta

from nephthys.utils.stats import calculate_daily_stats
from nephthys.utils.stats import calculate_overall_stats


async def get_leaderboard_view():
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
        f"{stats.mean_hang_time_minutes:.2f} minutes"
        if stats.mean_hang_time_minutes is not None
        else "No hang time data available"
    )
    avg_prev_day_hang_time_str = (
        f"{prev_day.mean_hang_time_minutes_unresolved:.2f} minutes"
        if prev_day.mean_hang_time_minutes_unresolved is not None
        else "No hang time data available"
    )

    return [
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Total Tickets*\nTotal: {stats.tickets_total}, Open: {stats.tickets_open}, In Progress: {stats.tickets_in_progress}, Closed: {stats.tickets_closed}\nHang time: {avg_hang_time_str}",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Past 24 Hours*\nTotal: {prev_day.new_tickets_total}, Open: {prev_day.new_tickets_still_open}, In Progress: {prev_day.assigned_today_in_progress}, Closed: {prev_day.closed_today}, Closed Today: {prev_day.closed_today_from_today}\nHang time: {avg_prev_day_hang_time_str}",
                },
            ],
        },
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
    ]
