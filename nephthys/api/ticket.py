from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse

from nephthys.database.tables import TeamTag
from nephthys.database.tables import Ticket


def user_to_json(user: dict[str, Any]) -> dict | None:
    # For some cursed reason, Piccolo will return dicts with all fields set to null
    # instead of just None, if the related record doesn't exist.
    if not user["id"]:
        return None

    return {
        "slack_id": user["slackId"],
        "id": user["id"],
        "username": user["username"],
    }


def ticket_to_json(ticket: dict[str, Any]) -> dict:
    """Converts a Ticket record (represented as a dict) to an API JSON format"""
    # I hate using dicts here because we get no type hinting :fear:
    return {
        "id": ticket["id"],
        "title": ticket["title"],
        "description": ticket["description"],
        "status": ticket["status"],
        "opened_by": user_to_json(ticket["openedById"]),
        "closed_by": user_to_json(ticket["closedById"]),
        "assigned_to": user_to_json(ticket["assignedToId"]),
        "reopened_by": user_to_json(ticket["reopenedById"]),
        "team_tags": [str(t) for t in ticket["team_tags"]],
        "created_at": ticket["createdAt"].isoformat(),
        "closed_at": ticket["closedAt"].isoformat() if ticket["closedAt"] else None,
        "message_ts": ticket["msgTs"],
    }


async def ticket_info(req: Request):
    try:
        ticket_id = int(req.query_params["id"])
    except KeyError:
        return JSONResponse({"error": "missing_ticket_id"}, status_code=400)
    except ValueError:
        return JSONResponse({"error": "invalid_ticket_id"}, status_code=400)
    ticket = (
        await Ticket.select(
            *Ticket.all_columns(),
            *Ticket.opened_by._.all_columns(),
            *Ticket.closed_by._.all_columns(),
            *Ticket.assigned_to._.all_columns(),
            *Ticket.reopened_by._.all_columns(),
            Ticket.team_tags(TeamTag.name),
        )
        .output(nested=True)
        .where(Ticket.id == ticket_id)
        .first()
    )

    if not ticket:
        return JSONResponse({"error": "ticket_not_found"}, status_code=404)
    print(ticket)
    return JSONResponse(ticket_to_json(ticket))
