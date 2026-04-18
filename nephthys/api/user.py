from starlette.requests import Request
from starlette.responses import JSONResponse

from nephthys.database.tables import Ticket
from nephthys.database.tables import User


async def user_stats(req: Request):
    user_id = req.query_params["id"]
    user = await User.objects().where(User.slack_id == user_id).first()
    if not user:
        return JSONResponse({"error": "user_not_found"}, status_code=404)

    closed_tickets = await Ticket.count().where(
        (Ticket.closed_by == user.id) & (Ticket.opened_by != user.id)
    )
    opened_tickets = await Ticket.count().where(Ticket.opened_by == user.id)

    return JSONResponse(
        {
            "tickets_opened": opened_tickets,
            "tickets_closed": closed_tickets,
            "helper": user.helper,
        }
    )
