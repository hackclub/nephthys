from starlette.requests import Request
from starlette.responses import JSONResponse

from nephthys.database.tables import TeamTag
from nephthys.database.tables import Ticket
from nephthys.database.tables import User


def user_to_json(user: User | None) -> dict | None:
    return (
        {"slack_id": user.slack_id, "id": user.id, "username": user.username}
        if user
        else None
    )


def tag_to_json(tag: TeamTag | None) -> str:
    if tag is None:
        raise ValueError("tag is None, did you forget to include the nested relation?")
    return tag.name


def ticket_to_json(ticket: Ticket, team_tags: list[TeamTag]) -> dict:
    return {
        "id": ticket.id,
        "title": ticket.title,
        "description": ticket.description,
        "status": ticket.status,
        "opened_by": user_to_json(ticket.opened_by),
        "closed_by": user_to_json(ticket.closed_by),
        "assigned_to": user_to_json(ticket.assigned_to),
        "reopened_by": user_to_json(ticket.reopened_by),
        "team_tags": [tag_to_json(t) for t in team_tags],
        "created_at": ticket.created_at.isoformat(),
        "closed_at": ticket.closed_at.isoformat() if ticket.closed_at else None,
        "message_ts": ticket.msg_ts,
    }


async def ticket_info(req: Request):
    try:
        ticket_id = int(req.query_params["id"])
    except KeyError:
        return JSONResponse({"error": "missing_ticket_id"}, status_code=400)
    except ValueError:
        return JSONResponse({"error": "invalid_ticket_id"}, status_code=400)
    ticket: Ticket | None = (
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

    team_tags: list[TeamTag] = await ticket.get_m2m(Ticket.team_tags)  # type: ignore - we have an list of TeamTags, but typechecker sees an array of Tables

    return JSONResponse(ticket_to_json(ticket, team_tags))
