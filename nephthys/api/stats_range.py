from datetime import datetime
from datetime import UTC

from starlette.requests import Request
from starlette.responses import JSONResponse

from nephthys.utils.stats import calculate_daily_stats


async def stats_range(req: Request):
    since = req.query_params.get("since") or req.query_params.get("after")
    if since:
        try:
            since = datetime.fromisoformat(since).astimezone(UTC)
        except ValueError:
            msg = f"not a valid ISO datetime: {since}"
            return JSONResponse({"error": msg}, status_code=400)
    else:
        since = datetime.fromtimestamp(0, UTC)

    until = req.query_params.get("until") or req.query_params.get("before")
    if until:
        try:
            until = datetime.fromisoformat(until).astimezone(UTC)
        except ValueError:
            msg = f"not a valid ISO datetime: {until}"
            return JSONResponse({"error": msg}, status_code=400)
    else:
        until = datetime.now(UTC)

    stats = await calculate_daily_stats(since, until)
    return JSONResponse(
        {
            "stats": stats.as_dict(),
            "since": since.isoformat(),
            "until": until.isoformat(),
        }
    )
