import pytz

from nephthys.utils.env import env
from nephthys.utils.performance import perf_timer
from nephthys.views.home.components.buttons import get_buttons
from nephthys.views.home.components.header import get_header
from nephthys.views.home.components.leaderboards import get_leaderboard_view
from nephthys.views.home.components.ticket_status_pie import get_ticket_status_pie_chart
from nephthys.views.home.error import get_error_view
from prisma.models import User


async def get_helper_view(user: User):
    async with perf_timer("Fetching user info"):
        user_info = await env.slack_client.users_info(user=user.slackId)
    if not user_info or not (slack_user := user_info.get("user")):
        return get_error_view(
            ":rac_freaking: oops, i couldn't find your info! try again in a bit?"
        )
    tz_string = slack_user.get("tz", "Europe/London")
    tz = pytz.timezone(tz_string)

    async with perf_timer("Rendering pie chart (total time)"):
        pie_chart = await get_ticket_status_pie_chart(tz)

    async with perf_timer("Generating leaderboard"):
        leaderboard = await get_leaderboard_view()

    header = get_header()
    btns = get_buttons(user, "dashboard")

    return {
        "type": "home",
        "blocks": [
            header,
            btns,
            {"type": "divider"},
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": ":rac_graph: funny circle and line things",
                    "emoji": True,
                },
            },
            pie_chart,
            *leaderboard,
        ],
    }
