from starlette.requests import Request
from starlette.responses import JSONResponse

from nephthys.database.tables import TagsOnTickets
from nephthys.database.tables import TeamTag
from nephthys.database.tables import Ticket
from nephthys.database.tables import User


def user_to_json(user: User | None) -> dict | None:
    return {"slack_id": user.slack_id, "id": user.id} if user else None


def tag_to_json(tag: TeamTag | None) -> str:
    if tag is None:
        raise ValueError("tag is None, did you forget to include the nested relation?")
    return tag.name


def ticket_to_json(
    ticket: Ticket, tag_links: list[TagsOnTickets] | None = None
) -> dict:
    if tag_links is None:
        raise ValueError("tag_links is None, did you forget to query TagsOnTickets?")
    return {
        "id": ticket.id,
        "title": ticket.title,
        "description": ticket.description,
        "status": ticket.status,
        "opened_by": user_to_json(ticket.opened_by),
        "closed_by": user_to_json(ticket.closed_by),
        "assigned_to": user_to_json(ticket.assigned_to),
        "reopened_by": user_to_json(ticket.reopened_by),
        "tags": [tag_to_json(t.tag) for t in tag_links],
        "created_at": ticket.created_at.isoformat(),
        "message_ts": ticket.msg_ts,
    }


async def ticket_info(req: Request):
    try:
        ticket_id = int(req.query_params["id"])
    except KeyError:
        return JSONResponse({"error": "missing_ticket_id"}, status_code=400)
    except ValueError:
        return JSONResponse({"error": "invalid_ticket_id"}, status_code=400)
    ticket = (
        await Ticket.objects(
            Ticket.opened_by,
            Ticket.closed_by,
            Ticket.assigned_to,
            Ticket.reopened_by,
        )
        .where(Ticket.id == ticket_id)
        .first()
    )

    if not ticket:
        return JSONResponse({"error": "ticket_not_found"}, status_code=404)

    tag_links = await TagsOnTickets.objects(TagsOnTickets.tag).where(
        TagsOnTickets.ticket == ticket_id
    )

    return JSONResponse(ticket_to_json(ticket, tag_links))
