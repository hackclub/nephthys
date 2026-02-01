from nephthys.utils.env import env
from prisma.models import User


def header_buttons(current_view: str, user: User | None):
    buttons = []

    buttons.append(
        {
            "type": "button",
            "text": {"type": "plain_text", "text": "Dashboard", "emoji": True},
            "action_id": "dashboard",
            **({"style": "primary"} if current_view != "dashboard" else {}),
        }
    )

    buttons.append(
        {
            "type": "button",
            "text": {"type": "plain_text", "text": "Assigned Tickets", "emoji": True},
            "action_id": "assigned-tickets",
            **({"style": "primary"} if current_view != "assigned-tickets" else {}),
        }
    )

    buttons.append(
        {
            "type": "button",
            "text": {"type": "plain_text", "text": "Team Tags", "emoji": True},
            "action_id": "team-tags",
            **({"style": "primary"} if current_view != "team-tags" else {}),
        }
    )

    buttons.append(
        {
            "type": "button",
            "text": {"type": "plain_text", "text": "My Stats", "emoji": True},
            "action_id": "my-stats",
            **({"style": "primary"} if current_view != "my-stats" else {}),
        }
    )

    if user and user.admin:
        buttons.append(
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Manage Category Tags",
                    "emoji": True,
                },
                "action_id": "manage-tags",
            }
        )

    blocks = {"type": "actions", "elements": buttons}
    return blocks


def title_line():
    return {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": f":rac_cute: {env.app_title}",
            "emoji": True,
        },
    }


def get_header(user: User | None, current: str = "dashboard") -> list[dict]:
    return [
        title_line(),
        header_buttons(current, user),
        {"type": "divider"},
    ]
