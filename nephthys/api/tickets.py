from datetime import datetime

from starlette.requests import Request
from starlette.responses import JSONResponse

from nephthys.api.ticket import ticket_to_json
from nephthys.database.enums import TicketStatus
from nephthys.database.tables import TeamTag
from nephthys.database.tables import Ticket


async def tickets_list(req: Request):
    filter_status = req.query_params.get("status")
    if filter_status:
        try:
            filter_status = TicketStatus(filter_status.upper())
        except ValueError:
            return JSONResponse(
                {"error": f"Invalid status parameter: {filter_status}"}, status_code=400
            )
    filter_created_after = req.query_params.get("since") or req.query_params.get(
        "after"
    )
    if filter_created_after:
        try:
            filter_created_after = datetime.fromisoformat(filter_created_after)
        except ValueError:
            msg = f"created_after parameter is not a valid ISO datetime: {filter_created_after}"
            return JSONResponse({"error": msg}, status_code=400)
    filter_created_before = req.query_params.get("until") or req.query_params.get(
        "before"
    )
    if filter_created_before:
        try:
            filter_created_before = datetime.fromisoformat(filter_created_before)
        except ValueError:
            msg = f"created_before parameter is not a valid ISO datetime: {filter_created_before}"
            return JSONResponse({"error": msg}, status_code=400)

    if (
        (not filter_status or filter_status == TicketStatus.CLOSED)
        and not filter_created_after
        and not filter_created_before
    ):
        # Prevent returning a massive number of tickets by default
        # If they want them, they should set a big date range explicitly
        # (that may also be disallowed in the future if it impacts performance too much)
        msg = "Provided filters are too broad"
        tip = "Please provide a ?since= or ?until= parameter, or filter by ?status=open or ?status=in_progress"
        return JSONResponse({"error": msg, "tip": tip}, status_code=400)

    query = Ticket.select(
        *Ticket.all_columns(),
        *Ticket.opened_by._.all_columns(),
        *Ticket.closed_by._.all_columns(),
        *Ticket.assigned_to._.all_columns(),
        *Ticket.reopened_by._.all_columns(),
        Ticket.team_tags(TeamTag.name),
    ).output(nested=True)

    if filter_status:
        query = query.where(Ticket.status == filter_status)
    if filter_created_after:
        query = query.where(Ticket.created_at >= filter_created_after)
    if filter_created_before:
        query = query.where(Ticket.created_at <= filter_created_before)

    tickets = await query.order_by(Ticket.created_at)

    return JSONResponse([ticket_to_json(t) for t in tickets])
