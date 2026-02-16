import logging

import pytz
from blockkit import Header
from blockkit import Home

from nephthys.utils.env import env
from nephthys.utils.performance import perf_timer
from nephthys.views.home.components.header import get_header_components
from nephthys.views.home.components.leaderboards import get_leaderboard_components
from nephthys.views.home.components.ticket_status_pie import (
    ticket_status_pie_chart_component,
)
from nephthys.views.home.error import get_error_view
from prisma.models import User


async def get_dashboard_view(slack_user: str, db_user: User | None):
    async with perf_timer("Fetching user info"):
        user_info_response = await env.slack_client.users_info(user=slack_user)
    user_info = user_info_response.get("user")
    if not user_info:
        logging.error(f"Failed to fetch user={slack_user}: {user_info_response}")
        return get_error_view(
            ":rac_freaking: oops, i couldn't find your info! try again in a bit?"
        )
    tz_string = user_info.get("tz")
    if not tz_string:
        logging.warning(f"No timezone found user={slack_user}")
        tz_string = "Europe/London"
    tz = pytz.timezone(tz_string)

    async with perf_timer("Rendering pie chart (total time)"):
        pie_chart = await ticket_status_pie_chart_component(tz)  # type: ignore (it works)

    async with perf_timer("Generating leaderboard"):
        leaderboard = await get_leaderboard_components()

    return Home(
        [
            *get_header_components(db_user, "dashboard"),
            Header(":rac_graph: funny circle and line things"),
            pie_chart,
            *leaderboard,
        ]
    ).build()
