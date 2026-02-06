from datetime import datetime
from datetime import timedelta

from starlette.requests import Request
from starlette.responses import JSONResponse

from nephthys.utils.stats import calculate_daily_stats
from nephthys.utils.stats import calculate_overall_stats


async def stats_v2(req: Request):
    """Stats endpoint, made as an improvement to /api/stats

    - Originally made to be used for the Flavortown Super Mega Dashboard
    - Subject to change depending on what's useful for dashboards
    """
    all_time_stats = await calculate_overall_stats()

    now = datetime.now().astimezone()
    one_day_ago = now - timedelta(days=1)
    current_day_stats = await calculate_daily_stats(one_day_ago, now)
    prev_day_stats = await calculate_daily_stats(
        one_day_ago - timedelta(days=1), one_day_ago
    )

    seven_days_ago = now - timedelta(days=7)
    current_week_stats = await calculate_daily_stats(seven_days_ago, now)
    prev_week_stats = await calculate_daily_stats(
        seven_days_ago - timedelta(days=7), seven_days_ago
    )

    return JSONResponse(
        {
            "all_time": all_time_stats.as_dict(),
            "past_24h": current_day_stats.as_dict(),
            "past_24h_previous": prev_day_stats.as_dict(),
            "past_7d": current_week_stats.as_dict(),
            "past_7d_previous": prev_week_stats.as_dict(),
        }
    )
