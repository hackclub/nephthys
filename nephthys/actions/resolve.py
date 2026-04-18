import logging
from datetime import datetime

from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.database.enums import TicketStatus
from nephthys.database.tables import Ticket
from nephthys.database.tables import User
from nephthys.utils.delete_thread import add_thread_to_delete_queue
from nephthys.utils.env import env
from nephthys.utils.logging import send_heartbeat
from nephthys.utils.permissions import can_resolve
from nephthys.utils.ticket_methods import delete_message
from nephthys.utils.ticket_methods import reply_to_ticket


async def resolve(
    ts: str,
    resolver: str,
    client: AsyncWebClient,
    stale: bool = False,
    add_reaction: bool = True,
    send_resolved_message: bool = True,
):
    resolving_user = await User.objects().where(User.slack_id == resolver).first()
    if not resolving_user:
        await send_heartbeat(
            f"User {resolver} attempted to resolve ticket with ts {ts} but isn't in the database.",
            messages=[f"Ticket TS: {ts}", f"Resolver ID: {resolver}"],
        )
        return

    allowed = await can_resolve(resolving_user.slack_id, resolving_user.id, ts)
    if not allowed:
        await send_heartbeat(
            f"User {resolver} attempted to resolve ticket with ts {ts} without permission.",
            messages=[f"Ticket TS: {ts}", f"Resolver ID: {resolver}"],
        )
        return
    ticket = (
        await Ticket.objects(Ticket.assigned_to)
        .where((Ticket.msg_ts == ts) & (Ticket.status != TicketStatus.CLOSED))
        .first()
    )
    if not ticket:
        logging.warning(
            f"Failed to resolve ticket ts={ts} because it's already closed or doesn't exist."
        )
        return

    if not resolving_user.helper and ticket.assigned_to:
        new_resolving_user = (
            await User.objects().where(User.id == ticket.assigned_to.id).first()
        )
        if new_resolving_user:
            resolving_user = new_resolving_user

    now = datetime.now()

    await Ticket.update(
        {
            Ticket.status: TicketStatus.CLOSED,
            Ticket.closed_by: resolving_user.id,
            Ticket.closed_at: now,
        }
    ).where(Ticket.msg_ts == ts)

    tkt = await Ticket.objects().where(Ticket.msg_ts == ts).first()
    if not tkt:
        await send_heartbeat(
            f"Failed to resolve ticket with ts {ts} by {resolver}. Ticket not found.",
            messages=[f"Ticket TS: {ts}", f"Resolver ID: {resolver}"],
        )
        return

    if send_resolved_message:
        await reply_to_ticket(
            ticket=tkt,
            client=client,
            text=(
                env.transcript.ticket_resolve.format(user_id=resolver)
                if not stale
                else env.transcript.ticket_resolve_stale.format(user_id=resolver)
            ),
        )
    if add_reaction:
        await client.reactions_add(
            channel=env.slack_help_channel,
            name="white_check_mark",
            timestamp=ts,
        )

    try:
        await client.reactions_remove(
            channel=env.slack_help_channel,
            name="thinking_face",
            timestamp=ts,
        )
    except SlackApiError as e:
        logging.error(
            f"Failed to remove thinking reaction from ticket with ts {ts}: {e.response['error']}"
        )

    if await env.workspace_admin_available():
        await add_thread_to_delete_queue(
            channel_id=env.slack_ticket_channel, thread_ts=tkt.ticket_ts
        )
    else:
        await delete_message(
            channel_id=env.slack_ticket_channel, message_ts=tkt.ticket_ts
        )

    logging.info(f"Resolved ticket ts={ts} resolving_user={resolving_user.slack_id}")
