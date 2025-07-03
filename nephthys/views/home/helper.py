import pytz

from nephthys.utils.env import env
from nephthys.views.home.components.buttons import get_buttons
from nephthys.views.home.components.leaderboards import get_leaderboard_view
from nephthys.views.home.components.ticket_status_pie import get_ticket_status_pie_chart
from nephthys.views.home.error import get_error_view
from prisma.enums import TicketStatus
from prisma.models import User


async def get_helper_view(user: User):
    tickets = await env.db.ticket.find_many() or []
    user_info = await env.slack_client.users_info(user=user.slackId)
    if not user_info or not (slack_user := user_info.get("user")):
        return get_error_view(
            ":rac_freaking: oops, i couldn't find your info! try again in a bit?"
        )
    tz_string = slack_user.get("tz", "Europe/London")
    tz = pytz.timezone(tz_string)

    pie_chart = await get_ticket_status_pie_chart(user, tz)
    leaderboard = await get_leaderboard_view(tz)

    organised_tkts = {}
    for ticket in tickets:
        status = ticket.status
        if status not in organised_tkts:
            organised_tkts[status] = []
        organised_tkts[status].append(ticket)

    formatted_msg = f"""
    *Requests*
    {len(tickets)} requests found
    {len(organised_tkts.get(TicketStatus.OPEN, []))} open
    {len(organised_tkts.get(TicketStatus.IN_PROGRESS, []))} in progress  ({len([ticket for ticket in tickets if ticket.status == TicketStatus.IN_PROGRESS and ticket.assignedToId == user.id])} assigned to you)
    {len(organised_tkts.get(TicketStatus.CLOSED, []))} closed  ({len([ticket for ticket in tickets if ticket.status == TicketStatus.CLOSED and ticket.closedById == user.id])} closed by you)
    """

    btns = get_buttons(user, "dashboard")

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
            {"type": "section", "text": {"type": "mrkdwn", "text": formatted_msg}},
            pie_chart,
            *leaderboard,
        ],
    }
