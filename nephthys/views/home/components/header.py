from blockkit import Button
from blockkit import Header

from nephthys.utils.env import env
from prisma.models import User


def header_buttons(current_view: str, user: User | None):
    buttons = []

    buttons.add_element(
        Button(
            "Dashboard",
            action_id="dashboard",
            style="primary" if current_view != "dashboard" else None,
        )
    )

    buttons.add_element(
        Button(
            "Assigned Tickets",
            action_id="assigned-tickets",
            style="primary" if current_view != "assigned-tickets" else None,
        )
    )

    buttons.add_element(
        Button(
            "Team Tags",
            action_id="team-tags",
            style="primary" if current_view != "team-tags" else None,
        )
    )

    buttons.add_element(
        Button(
            "My Stats",
            action_id="my-stats",
            style="primary" if current_view != "my-stats" else None,
        )
    )

    return buttons.build()


def title_line():
    return Header(f":rac_cute: {env.app_title}").build()


def get_header(user: User | None, current: str = "dashboard") -> list[dict]:
    return [
        title_line(),
        header_buttons(current, user),
        {"type": "divider"},
    ]
