from nephthys.utils.env import env
from prisma.models import User


def header_buttons(current_view: str):
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
            "text": {"type": "plain_text", "text": "Tags", "emoji": True},
            "action_id": "tags",
            **({"style": "primary"} if current_view != "tags" else {}),
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


def get_header(user: User, current: str = "dashboard"):
    return [
        title_line(),
        header_buttons(current),
        {"type": "divider"},
    ]
