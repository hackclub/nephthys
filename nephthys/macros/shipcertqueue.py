from nephthys.actions.resolve import resolve
from nephthys.database.tables import User
from nephthys.macros.types import Macro
from nephthys.utils.env import env
from nephthys.utils.slack_user import get_user_profile
from nephthys.utils.ticket_methods import reply_to_ticket


class ShipCertQueue(Macro):
    name = "shipqueue"
    aliases = ["shipcert", "shipcertqueue"]

    async def run(self, ticket, helper, **kwargs):
        """
        A simple macro telling people about the ship certification backlog
        """
        macro_text = env.transcript.ship_cert_queue_macro
        if not macro_text:
            # Not all events have this macro
            await env.slack_client.chat_postEphemeral(
                channel=env.slack_help_channel,
                thread_ts=ticket.msg_ts,
                user=helper.slack_id,
                text=f"Invalid macro: The `{self.name}` macro is not configured for this channel.",
            )
            return
        sender = await User.objects().where(User.id == ticket.opened_by).first()
        if not sender:
            return
        user = await get_user_profile(sender.slack_id)
        await reply_to_ticket(
            text=macro_text.replace("(user)", user.display_name()),
            ticket=ticket,
            client=env.slack_client,
        )
        await resolve(
            ts=ticket.msg_ts,
            resolver=helper.slack_id,
            client=env.slack_client,
            send_resolved_message=False,
        )
