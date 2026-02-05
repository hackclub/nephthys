from starlette.requests import Request
from starlette.responses import JSONResponse

from nephthys.utils.env import env
from prisma.models import Tag
from prisma.models import Ticket
from prisma.models import User


def user_to_json(user: User | None) -> dict | None:
    return {"slack_id": user.slackId, "id": user.id} if user else None


def tag_to_json(tag: Tag | None) -> str:
    if tag is None:
        raise ValueError("tag is None, did you forget to include the nested relation?")
    return tag.name


def ticket_to_json(ticket: Ticket) -> dict:
    if ticket.tagsOnTickets is None:
        raise ValueError(
            "ticket.tagsOnTickets is None, did you forget to include the relation?"
        )
    return {
        "id": ticket.id,
        "title": ticket.title,
        "description": ticket.description,
        "status": ticket.status,
        "opened_by": user_to_json(ticket.openedBy),
        "closed_by": user_to_json(ticket.closedBy),
        "assigned_to": user_to_json(ticket.assignedTo),
        "reopened_by": user_to_json(ticket.reopenedBy),
        "tags": [tag_to_json(t.tag) for t in ticket.tagsOnTickets],
        "created_at": ticket.createdAt.isoformat(),
        "message_ts": ticket.msgTs,
    }


async def ticket_info(req: Request):
    try:
        ticket_id = int(req.query_params["id"])
    except KeyError:
        return JSONResponse({"error": "missing_ticket_id"}, status_code=400)
    except ValueError:
        return JSONResponse({"error": "invalid_ticket_id"}, status_code=400)
    ticket = await env.db.ticket.find_unique(
        where={"id": ticket_id},
        include={
            "openedBy": True,
            "closedBy": True,
            "assignedTo": True,
            "reopenedBy": True,
            "tagsOnTickets": {"include": {"tag": True}},
        },
    )

    if not ticket:
        return JSONResponse({"error": "ticket_not_found"}, status_code=404)

    return JSONResponse(ticket_to_json(ticket))
