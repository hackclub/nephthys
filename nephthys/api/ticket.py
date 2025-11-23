from starlette.requests import Request
from starlette.responses import JSONResponse

from nephthys.utils.env import env


async def ticket_info(req: Request):
    try:
        ticket_id = int(req.query_params["id"])
    except KeyError:
        return JSONResponse({"error": "missing_ticket_id"}, status_code=400)
    except ValueError:
        return JSONResponse({"error": "invalid_ticket_id"}, status_code=400)
    ticket = await env.db.ticket.find_unique(
        where={"id": ticket_id},
        include={"openedBy": True, "closedBy": True, "assignedTo": True},
    )

    if not ticket:
        return JSONResponse({"error": "ticket_not_found"}, status_code=404)

    return JSONResponse(
        {
            "title": ticket.title,
            "description": ticket.description,
            "status": ticket.status,
            "opened_by": {"slack_id": ticket.openedBy.slackId}
            if ticket.openedBy
            else None,
            "closed_by": {"slack_id": ticket.closedBy.slackId}
            if ticket.closedBy
            else None,
            "assigned_to": {"slack_id": ticket.assignedTo.slackId}
            if ticket.assignedTo
            else None,
            "created_at": ticket.createdAt.isoformat(),
        }
    )
