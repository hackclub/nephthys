from nephthys.actions.resolve import resolve
from nephthys.macros.types import Macro
from nephthys.utils.env import env
from nephthys.utils.slack_user import get_user_profile
from nephthys.utils.ticket_methods import reply_to_ticket


class Identity(Macro):
    name = "identity"

    async def run(self, ticket, helper, **kwargs):
        """
        A simple macro telling people to use the identity help channel
        """
        sender = await env.db.user.find_first(where={"id": ticket.openedById})
        if not sender:
            return
        user = await get_user_profile(sender.slackId)
        await reply_to_ticket(
            text=env.transcript.identity_macro.replace("(user)", user.display_name()),
            ticket=ticket,
            client=env.slack_client,
        )
        await resolve(
            ts=ticket.msgTs,
            resolver=helper.slackId,
            client=env.slack_client,
            send_resolved_message=False,
        )
