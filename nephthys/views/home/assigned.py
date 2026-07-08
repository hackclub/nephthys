import pytz
from blockkit import Actions
from blockkit import Button
from blockkit import Divider
from blockkit import Header
from blockkit import Home
from blockkit import Section

from nephthys.database.enums import TicketStatus
from nephthys.database.tables import Ticket
from nephthys.database.tables import User
from nephthys.utils.ticket_methods import get_question_message_link
from nephthys.views.home import AppHomeView
from nephthys.views.home.components.error_screen import error_screen
from nephthys.views.home.components.header import get_header_components

# Each ticket needs 2 blocks, and the heading takes up 3 blocks.
# Maximum blocks per view is 100.
TICKETS_PER_PAGE = 48


def pagination_buttons(page: int, total_pages: int) -> Actions:
    buttons = Actions()
    for p in range(1, total_pages + 1):
        buttons.add_element(
            Button(
                text=str(p),
                action_id="assigned-tickets-page",
                value=str(p),
                style=Button.PRIMARY if p == page else None,
            )
        )
    return buttons


async def get_assigned_tickets_view(user: User | None, page: int = 1):
    header = get_header_components(user, AppHomeView.ASSIGNED_TICKETS)

    if not user or not user.helper:
        return error_screen(
            header,
            ":rac_info: you're not a helper!",
            ":rac_believes_in_theory_about_green_lizards_and_space_lasers: only helpers can be assigned to tickets, so you have none - zero responsibility!",
        )

    total = await Ticket.count().where(
        (Ticket.assigned_to == user.id) & (Ticket.status != TicketStatus.CLOSED)
    )

    if total == 0:
        return error_screen(
            header,
            ":rac_cute: no assigned tickets",
            ":rac_believes_in_theory_about_green_lizards_and_space_lasers: you don't have any assigned tickets right now!",
        )

    total_pages = (total + TICKETS_PER_PAGE - 1) // TICKETS_PER_PAGE
    page = max(1, min(page, total_pages))

    tickets = (
        await Ticket.objects(Ticket.opened_by)
        .where((Ticket.assigned_to == user.id) & (Ticket.status != TicketStatus.CLOSED))
        .order_by(Ticket.created_at, ascending=True)
        .limit(TICKETS_PER_PAGE)
        .offset((page - 1) * TICKETS_PER_PAGE)
    )

    ticket_blocks = []
    for ticket in tickets:
        unix_ts = int(ticket.created_at.timestamp())
        time_ago_str = f"<!date^{unix_ts}^opened {{ago}}|at {ticket.created_at.astimezone(pytz.timezone('Europe/London')).strftime('%H:%M %Z')}>"
        opened_by_str = (
            f"<@{ticket.opened_by.slack_id}>" if ticket.opened_by else "unknown user"
        )
        ticket_blocks.append(
            Section(
                text=f"*{ticket.title}*\n _from {opened_by_str}. {time_ago_str}_",
                accessory=Button(
                    text=":rac_info: view ticket",
                    action_id=f"view-ticket-{ticket.msg_ts}",
                    url=get_question_message_link(ticket),
                    value=ticket.msg_ts,
                ),
            )
        )
        ticket_blocks.append(Divider())

    if total_pages > 1:
        ticket_blocks.append(pagination_buttons(page, total_pages))

    return Home(
        [
            *header,
            Header(":rac_cute: here are your assigned tickets <3"),
            *ticket_blocks,
        ]
    ).build()
