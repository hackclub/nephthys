import logging

from slack_sdk.errors import SlackApiError

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
        thread_url = get_question_message_link(ticket)

        backend_message = await env.slack_client.chat_postMessage(
            channel=env.slack_ticket_channel,
            text=f"Reopened ticket from <@{author_id}>: {ticket.description}",
            blocks=[
                {
                    "type": "input",
                    "label": {
                        "type": "plain_text",
                        "text": "Tag ticket",
                        "emoji": True,
                    },
                    "element": {
                        "action_id": "tag-list",
                        "type": "multi_external_select",
                        "placeholder": {"type": "plain_text", "text": "Select tags"},
                        "min_query_length": 0,
                    },
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Reopened by <@{helper.slackId}>. Originally submitted by <@{author_id}>. <{thread_url}|View thread>.",
                        }
                    ],
                },
            ],
            username=author.display_name(),
            icon_url=author.profile_pic_512x() or "",
            unfurl_links=True,
            unfurl_media=True,
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
