import logging
from datetime import datetime
from datetime import timedelta

from blockkit import Actions
from blockkit import Button
from blockkit import Section
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

THREAD_CREDIT_CUTOFF = timedelta(hours=48)


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
        await client.chat_postEphemeral(
            channel=env.slack_help_channel,
            thread_ts=ts,
            user=resolver,
            text="Only helpers or the original poster can mark this thread as resolved.",
        )
        return

    ticket = await Ticket.objects(Ticket.assigned_to).get((Ticket.msg_ts == ts))
    if not ticket:
        raise ValueError(f"Failed to find ticket with ts {ts}")
    if ticket.status == TicketStatus.CLOSED:
        await client.chat_postEphemeral(
            channel=env.slack_help_channel,
            thread_ts=ticket.msg_ts,
            user=resolver,
            text="Cannot mark as resolved — this ticket is already resolved!",
        )
        return

    now = datetime.now()

    # If the last message in the thread is recent, credit goes to the last
    # helper who replied (ticket.assigned_to) rather than whoever clicked
    # resolve. This prevents rewarding "stealing" active threads, while
    # still rewarding closing stale, already-answered threads.
    credit_user = resolving_user
    if (
        ticket.assigned_to
        and ticket.last_msg_at is not None
        and (now - ticket.last_msg_at) <= THREAD_CREDIT_CUTOFF
    ):
        credit_user = ticket.assigned_to
    elif not resolving_user.helper and ticket.assigned_to:
        credit_user = ticket.assigned_to

    await Ticket.update(
        {
            Ticket.status: TicketStatus.CLOSED,
            Ticket.closed_by: credit_user.id,
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

    # Build the "ticket resolved!" message
    text = (
        env.transcript.ticket_resolve.format(user_id=credit_user.slack_id)
        if not stale
        else env.transcript.ticket_resolve_stale.format(user_id=credit_user.slack_id)
    )
    actions = Actions()
    if env.enable_feedback:
        actions.add_element(
            Button(
                text="Give feedback",
                action_id="feedback-button",
                value=f"{tkt.id}",
            )
        )
    actions.add_element(
        Button(
            text="Re-open thread",
            action_id="reopen-button",
            value=f"{tkt.id}",
        )
    )

    if send_resolved_message:
        await reply_to_ticket(
            ticket=tkt,
            client=client,
            text=text,
            blocks=[Section(text), actions],
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

    logging.info(
        f"Resolved ticket ts={ts} by slack_id={resolving_user.slack_id} credit_to={credit_user.slack_id}"
    )
