import pytz

from nephthys.database.enums import TicketStatus
from nephthys.database.tables import Ticket
from nephthys.database.tables import User
from nephthys.utils.ticket_methods import get_question_message_link
from nephthys.views.home.components.error_screen import error_screen
from nephthys.views.home.components.header import get_header


async def get_assigned_tickets_view(user: User | None):
    header = get_header(user, "assigned-tickets")

    if not user or not user.helper:
        return error_screen(
            header,
            ":rac_info: you're not a helper!",
            ":rac_believes_in_theory_about_green_lizards_and_space_lasers: only helpers can be assigned to tickets, so you have none - zero responsibility!",
        )

    tickets = await Ticket.objects(Ticket.opened_by).where(
        (Ticket.assigned_to == user.id) & (Ticket.status != TicketStatus.CLOSED)
    )

    if not tickets:
        return error_screen(
            header,
            ":rac_cute: no assigned tickets",
            ":rac_believes_in_theory_about_green_lizards_and_space_lasers: you don't have any assigned tickets right now!",
        )

    ticket_blocks = []
    for ticket in tickets:
        unix_ts = int(ticket.created_at.timestamp())
        time_ago_str = f"<!date^{unix_ts}^opened {{ago}}|at {ticket.created_at.astimezone(pytz.timezone('Europe/London')).strftime('%H:%M %Z')}>"
        opened_by_str = (
            f"<@{ticket.opened_by.slack_id}>" if ticket.opened_by else "unknown user"
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
                    "action_id": f"view-ticket-{ticket.msg_ts}",
                    "url": get_question_message_link(ticket),
                    "value": ticket.msg_ts,
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
