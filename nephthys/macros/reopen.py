import logging

from slack_sdk.errors import SlackApiError

from nephthys.events.message.send_backend_message import send_backend_message
from nephthys.macros.types import Macro
from nephthys.utils.env import env
from nephthys.utils.logging import send_heartbeat
from nephthys.utils.slack_user import get_user_profile
from nephthys.utils.ticket_methods import get_question_message_link
from nephthys.utils.ticket_methods import reply_to_ticket
from prisma.enums import TicketStatus


class Reopen(Macro):
    name = "reopen"
    aliases = ["unresolve", "open"]
    can_run_on_closed = True

    async def run(self, ticket, helper, **kwargs):
        """
        A simple macro to reopen a closed ticket
        """
        if ticket.status != TicketStatus.CLOSED:
            return

        await env.db.ticket.update(
            where={"id": ticket.id},
            data={
                "status": TicketStatus.OPEN,
                "closedBy": {"disconnect": True},
                "closedAt": None,
            },
        )

        await reply_to_ticket(
            text=env.transcript.ticket_reopen.format(helper_slack_id=helper.slackId),
            ticket=ticket,
            client=env.slack_client,
        )

        if not ticket.openedBy:
            await send_heartbeat(
                f"Attempted to reopen ticket (TS {ticket.msgTs}) but ticket author has not been recorded"
            )
            return
        author_id = ticket.openedBy.slackId
        author = await get_user_profile(author_id)
        other_tickets = await env.db.ticket.count(
            where={
                "openedById": ticket.openedById,
                "id": {"not": ticket.id},
            }
        )

        backend_message = await send_backend_message(
            author_user_id=author_id,
            description=ticket.description,
            msg_ts=ticket.msgTs,
            past_tickets=other_tickets,
            client=env.slack_client,
            current_question_tag_id=ticket.questionTagId,
            reopened_by=helper,
            display_name=author.display_name(),
            profile_pic=author.profile_pic_512x(),
        )

        new_ticket_ts = backend_message["ts"]
        if not new_ticket_ts:
            logging.error(f"Invalid Slack message creation response: {backend_message}")
            raise ValueError("Invalid Slack message creation response: no ts")
        await env.db.ticket.update(
            where={"id": ticket.id},
            data={"ticketTs": new_ticket_ts},
        )

        try:
            await env.slack_client.reactions_remove(
                channel=env.slack_help_channel,
                name="white_check_mark",
                timestamp=ticket.msgTs,
            )
        except SlackApiError as e:
            logging.error(
                f"Failed to remove check reaction from ticket with ts {ticket.msgTs}: {e.response['error']}"
            )
        await env.slack_client.reactions_add(
            channel=env.slack_help_channel,
            name="thinking_face",
            timestamp=ticket.msgTs,
        )

        await send_heartbeat(
            f"Ticket {ticket.id} reopened by <@{helper.slackId}>",
            messages=[
                f"Ticket ID: {ticket.id}",
                f"Original TS: {ticket.msgTs}",
                f"New TS: {new_ticket_ts}",
            ],
        )
