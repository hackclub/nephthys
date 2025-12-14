from datetime import datetime
from datetime import timedelta

from starlette.requests import Request
from starlette.responses import JSONResponse

from nephthys.utils.stats import calculate_daily_stats
from nephthys.utils.stats import calculate_overall_stats


async def stats(req: Request):
    total_stats = await calculate_overall_stats()
    now = datetime.now().astimezone()
    one_day_ago = now - timedelta(days=1)
    prev_day_stats = await calculate_daily_stats(one_day_ago, now)

    return JSONResponse(
        {
            "total_tickets": total_stats.tickets_total,
            "total_open": total_stats.tickets_open,
            "total_in_progress": total_stats.tickets_in_progress,
            "total_closed": total_stats.tickets_closed,
            "total_top_3_users_with_closed_tickets": [
                {
                    "user_id": entry["user"].id,
                    "slack_id": entry["user"].slackId,
                    "closed_ticket_count": entry["count"],
                }
                for entry in total_stats.helpers_leaderboard[:3]
            ],
            "average_hang_time_minutes": total_stats.avg_hang_time_minutes,
            "prev_day_total": prev_day_stats.new_tickets_total,
            "prev_day_open": prev_day_stats.new_tickets_still_open,
            "prev_day_in_progress": prev_day_stats.new_tickets_in_progress,
            "prev_day_closed": prev_day_stats.new_tickets_now_closed,
            "prev_day_top_3_users_with_closed_tickets": [
                {
                    "user_id": entry["user"].id,
                    "slack_id": entry["user"].slackId,
                    "closed_ticket_count": entry["count"],
                }
                for entry in prev_day_stats.helpers_leaderboard[:3]
            ],
            "prev_day_average_hang_time_minutes": prev_day_stats.avg_hang_time_minutes,
        }
    )
