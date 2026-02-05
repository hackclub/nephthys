from datetime import datetime

from starlette.requests import Request
from starlette.responses import JSONResponse

from nephthys.utils.env import env
from prisma.enums import TicketStatus
from prisma.models import Ticket
from prisma.models import User
from prisma.types import TicketWhereInput


def user_to_json(user: User | None) -> dict | None:
    return {"slack_id": user.slackId, "id": user.id} if user else None


def ticket_to_json(ticket: Ticket) -> dict:
    return {
        "title": ticket.title,
        "description": ticket.description,
        "status": ticket.status,
        "opened_by": user_to_json(ticket.openedBy),
        "closed_by": user_to_json(ticket.closedBy),
        "assigned_to": user_to_json(ticket.assignedTo),
        "created_at": ticket.createdAt.isoformat(),
    }


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

    db_filter: TicketWhereInput = {}
    if filter_status:
        db_filter["status"] = filter_status
    if filter_created_after or filter_created_before:
        db_filter["createdAt"] = {}
        if filter_created_after:
            db_filter["createdAt"]["gte"] = filter_created_after
        if filter_created_before:
            db_filter["createdAt"]["lte"] = filter_created_before

    tickets = await env.db.ticket.find_many(
        where=db_filter,
        include={
            "openedBy": True,
            "closedBy": True,
            "assignedTo": True,
            "reopenedBy": True,
            "tagsOnTickets": True,
        },
    )
    return JSONResponse([ticket_to_json(t) for t in tickets])
