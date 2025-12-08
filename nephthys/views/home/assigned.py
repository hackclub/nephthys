import pytz

from nephthys.utils.env import env
from nephthys.views.home.components.error_screen import error_screen
from nephthys.views.home.components.header import get_header
from prisma.enums import TicketStatus
from prisma.models import User


async def get_assigned_tickets_view(user: User | None):
    header = get_header(user, "assigned-tickets")

    if not user or not user.helper:
        return error_screen(
            header,
            ":rac_info: you're not a helper!",
            ":rac_believes_in_theory_about_green_lizards_and_space_lasers: only helpers can be assigned to tickets, so you have none - zero responsibility!",
        )

    tickets = await env.db.ticket.find_many(
        where={"assignedToId": user.id, "NOT": [{"status": TicketStatus.CLOSED}]},
        include={"openedBy": True},
    )

    if not tickets:
        return error_screen(
            header,
            ":rac_cute: no assigned tickets",
            ":rac_believes_in_theory_about_green_lizards_and_space_lasers: you don't have any assigned tickets right now!",
        )

    ticket_blocks = []
    for ticket in tickets:
        unix_ts = int(ticket.createdAt.timestamp())
        time_ago_str = f"<!date^{unix_ts}^opened {{ago}}|at {ticket.createdAt.astimezone(pytz.timezone('Europe/London')).strftime('%H:%M %Z')}>"
        opened_by_str = (
            f"<@{ticket.openedBy.slackId}>" if ticket.openedBy else "unknown user"
        )
        ticket_blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{ticket.title}*\n _from {opened_by_str}. {time_ago_str}_",
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": ":rac_info: view ticket",
                        "emoji": True,
                    },
                    "action_id": f"view-ticket-{ticket.msgTs}",
                    "url": f"https://hackclub.slack.com/archives/{env.slack_help_channel}/p{ticket.msgTs.replace('.', '')}",
                    "value": ticket.msgTs,
                },
            }
        )
        ticket_blocks.append({"type": "divider"})

    return {
        "type": "home",
        "blocks": [
            *header,
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": ":rac_cute: here are your assigned tickets <3",
                    "emoji": True,
                },
            },
            *ticket_blocks,
        ],
    }
