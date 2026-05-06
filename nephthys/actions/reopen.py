import logging
from datetime import datetime

from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.database.enums import TicketStatus
from nephthys.database.tables import Ticket
from nephthys.database.tables import User
from nephthys.errors.errors import PermissionDenied
from nephthys.errors.errors import TicketNotClosedError
from nephthys.events.message.send_backend_message import send_backend_message
from nephthys.utils.env import env
from nephthys.utils.logging import send_heartbeat
from nephthys.utils.permissions import can_resolve
from nephthys.utils.slack_user import get_user_profile
from nephthys.utils.ticket_methods import reply_to_ticket


async def reopen(ticket: Ticket, reopened_by: User, client: AsyncWebClient):
    """The opposite of resolving! Makes a resolved ticket open again

    Checks if the user user is allowed to reopen the ticket, raising a
    `PermissionDenied` error if not.
    """
    if ticket.status != TicketStatus.CLOSED:
        raise TicketNotClosedError(ticket.id)
    if not await can_resolve(reopened_by.slack_id, reopened_by.id, ticket.msg_ts):
        raise PermissionDenied(
            "Only helpers or the original author can reopen a ticket",
            user_id=reopened_by.id,
        )

    await Ticket.update(
        {
            Ticket.status: TicketStatus.OPEN,
            Ticket.closed_by: None,
            Ticket.reopened_by: reopened_by,
            Ticket.reopened_at: datetime.now(),
            Ticket.closed_at: None,
        }
    ).where(Ticket.id == ticket.id)

    await reply_to_ticket(
        text=env.transcript.ticket_reopen.format(helper_slack_id=reopened_by.slack_id),
        ticket=ticket,
        client=env.slack_client,
    )

    if not (author := await User.objects().get(User.id == ticket.opened_by)):
        raise ValueError("Cannot reopen ticket with no recorded author")
    author_profile = await get_user_profile(author.slack_id)
    other_tickets = await Ticket.count().where(
        (Ticket.opened_by == ticket.opened_by) & (Ticket.id != ticket.id)
    )

    backend_message = await send_backend_message(
        author_user_id=author.slack_id,
        description=ticket.description,
        msg_ts=ticket.msg_ts,
        past_tickets=other_tickets,
        client=env.slack_client,
        current_category_tag_id=ticket.category_tag,
        reopened_by=reopened_by,
        display_name=author_profile.display_name(),
        profile_pic=author_profile.profile_pic_512x(),
    )

    new_ticket_ts = backend_message["ts"]
    if not new_ticket_ts:
        logging.error(f"Invalid Slack message creation response: {backend_message}")
        raise ValueError("Invalid Slack message creation response: no ts")
    await Ticket.update(
        {
            Ticket.ticket_ts: new_ticket_ts,
        }
    ).where(Ticket.id == ticket.id)

    try:
        await env.slack_client.reactions_remove(
            channel=env.slack_help_channel,
            name="white_check_mark",
            timestamp=ticket.msg_ts,
        )
    except SlackApiError as e:
        logging.error(
            f"Failed to remove check reaction from ticket with ts {ticket.msg_ts}: {e.response['error']}"
        )
    await env.slack_client.reactions_add(
        channel=env.slack_help_channel,
        name="thinking_face",
        timestamp=ticket.msg_ts,
    )

    await send_heartbeat(
        f"Ticket {ticket.id} reopened by <@{reopened_by.slack_id}>",
        messages=[
            f"Ticket ID: {ticket.id}",
            f"Original TS: {ticket.msg_ts}",
            f"New TS: {new_ticket_ts}",
        ],
    )
