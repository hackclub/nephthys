from nephthys.macros.types import Macro
from nephthys.utils.env import env
from nephthys.utils.logging import send_heartbeat
from nephthys.utils.ticket_methods import reply_to_ticket
from prisma.enums import TicketStatus


class Reopen(Macro):
    name = "reopen"
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

        user_info = await env.slack_client.users_info(user=ticket.openedBy.slackId)
        name = (
            user_info["user"]["profile"]["display_name"]
            or user_info["user"]["real_name"]
            or "Explorer"
        )
        profile_pic = user_info["user"]["profile"].get("image_512", "")
        thread_url = f"https://hackclub.slack.com/archives/{env.slack_help_channel}/p{ticket.msgTs.replace('.', '')}"

        backend_message = await env.slack_client.chat_postMessage(
            channel=env.slack_ticket_channel,
            text=f"Reopened ticket from <@{ticket.openedBy.slackId}>: {ticket.description}",
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
                            "text": f"Reopened by <@{helper.slackId}>. Originally submitted by <@{ticket.openedBy.slackId}>. <{thread_url}|View thread>.",
                        }
                    ],
                },
            ],
            username=name,
            icon_url=profile_pic,
            unfurl_links=True,
            unfurl_media=True,
        )

        new_ticket_ts = backend_message["ts"]
        await env.db.ticket.update(
            where={"id": ticket.id},
            data={"ticketTs": new_ticket_ts},
        )

        await env.slack_client.reactions_remove(
            channel=env.slack_help_channel,
            name="white_check_mark",
            timestamp=ticket.msgTs,
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
