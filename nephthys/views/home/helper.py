import logging
from time import perf_counter

import pytz

from nephthys.utils.env import env
from nephthys.views.home.components.buttons import get_buttons
from nephthys.views.home.components.leaderboards import get_leaderboard_view
from nephthys.views.home.components.ticket_status_pie import get_ticket_status_pie_chart
from nephthys.views.home.error import get_error_view
from prisma.models import User


async def get_helper_view(user: User):
    time_start = perf_counter()
    user_info = await env.slack_client.users_info(user=user.slackId)
    time_user_info = perf_counter()
    logging.info(f"Fetched user info in {time_user_info - time_start:.4f} seconds")
    if not user_info or not (slack_user := user_info.get("user")):
        return get_error_view(
            ":rac_freaking: oops, i couldn't find your info! try again in a bit?"
        )
    tz_string = slack_user.get("tz", "Europe/London")
    tz = pytz.timezone(tz_string)

    pie_chart = await get_ticket_status_pie_chart(tz)
    time_pie_chart = perf_counter()
    logging.info(f"Rendered pie chart in {time_pie_chart - time_user_info:.4f} seconds")
    leaderboard = await get_leaderboard_view()
    time_leaderboard = perf_counter()
    logging.info(
        f"Generated leaderboard in {time_leaderboard - time_pie_chart:.4f} seconds"
    )

    btns = get_buttons(user, "dashboard")
    logging.info(
        f"Generated Dashboard view in {perf_counter() - time_start:.4f} seconds"
    )

    return {
        "type": "home",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": ":rac_cute: helper heidi",
                    "emoji": True,
                },
            },
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
