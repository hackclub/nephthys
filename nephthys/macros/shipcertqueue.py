from nephthys.actions.resolve import resolve
from nephthys.macros.types import Macro
from nephthys.utils.env import env
from nephthys.utils.slack_user import get_user_profile
from nephthys.utils.ticket_methods import reply_to_ticket


class ShipCertQueue(Macro):
    name = "shipcertqueue"

    async def run(self, ticket, helper, **kwargs):
        """
        A simple macro telling people about the ship certification backlog
        """
        macro_text = env.transcript.ship_cert_queue_macro
        if not macro_text:
            # Not all events have this macro
            await env.slack_client.chat_postEphemeral(
                channel=env.slack_help_channel,
                thread_ts=ticket.msgTs,
                user=helper.slackId,
                text=f"Invalid macro: The `{self.name}` macro is not configured for this channel.",
            )
            return
        sender = await env.db.user.find_first(where={"id": ticket.openedById})
        if not sender:
            return
        user = await get_user_profile(sender.slackId)
        await reply_to_ticket(
            text=macro_text.replace("(user)", user.display_name()),
            ticket=ticket,
            client=env.slack_client,
        )
        await resolve(
            ts=ticket.msgTs,
            resolver=helper.slackId,
            client=env.slack_client,
            send_resolved_message=False,
        )
