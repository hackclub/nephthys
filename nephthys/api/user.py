from starlette.requests import Request
from starlette.responses import JSONResponse

from nephthys.utils.env import env


async def user_stats(req: Request):
    user_id = req.query_params["id"]
    user = await env.db.user.find_unique(where={"slackId": user_id})
    if not user:
        return JSONResponse({"error": "user_not_found"}, status_code=404)

    closed_tickets = await env.db.ticket.count(where={"closedById": user.id})
    opened_tickets = await env.db.ticket.count(where={"openedById": user.id})

    return JSONResponse(
        {"tickets_opened": opened_tickets, "tickets_closed": closed_tickets}
    )
