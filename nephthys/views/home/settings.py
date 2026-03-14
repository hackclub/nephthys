from blockkit import Actions
from blockkit import Button
from blockkit import Divider
from blockkit import Header
from blockkit import Home
from blockkit import Section

from nephthys.utils.env import env
from nephthys.views.home.components.header import get_header_components
from prisma.models import User


async def get_settings_view(user: User | None) -> dict:
    is_admin = bool(user and user.admin)

    header = get_header_components(user, "settings")

    if not is_admin:
        return Home(
            [
                *header,
                Header(":rac_info: Settings"),
                Section(":rac_nooo: only admins can manage settings."),
            ]
        ).build()

    stale_days_setting = await env.db.settings.find_unique(
        where={"key": "stale_ticket_days"}
    )
    current_stale_days = stale_days_setting.value if stale_days_setting else "Not set"

    stale_enabled = stale_days_setting and stale_days_setting.value

    return Home(
        [
            *header,
            Header(":rac_wrench: Bot Settings"),
            Section(":rac_thumbs: configure bot behavior and features"),
            Divider(),
            Section(
                text=f"*Stale Ticket Auto-Close*\n"
                f"Automatically close tickets after a period of inactivity.\n"
                f"Current setting: *{current_stale_days}* {'day' if current_stale_days == '1' else 'days'} "
                f"{'(Enabled)' if stale_enabled else '(Disabled)'}"
            ),
            Actions(
                elements=[
                    Button(
                        text=":pencil2: Configure",
                        action_id="configure-stale-days"
                        if stale_enabled
                        else "toggle-stale-feature",
                        value="enable" if not stale_enabled else None,
                        style=Button.PRIMARY,
                    ),
                ]
                + (
                    [
                        Button(
                            text=":x: Disable",
                            action_id="toggle-stale-feature",
                            value="disable",
                            style=Button.DANGER,
                        ),
                    ]
                    if stale_enabled
                    else []
                )
            ),
            Divider(),
        ]
    ).build()
