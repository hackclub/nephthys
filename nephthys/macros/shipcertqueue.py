from nephthys.actions.resolve import resolve
from nephthys.macros.types import Macro
from nephthys.utils.env import env
from nephthys.utils.slack_user import get_user_name
from nephthys.utils.ticket_methods import reply_to_ticket


class ShipCertQueue(Macro):
    name = "shipcertqueue"

    async def run(self, ticket, helper, **kwargs):
        """
        A simple macro telling people about the ship certification backlog
        """
        sender = await env.db.user.find_first(where={"id": ticket.openedById})
        if not sender:
            return
        user_name = await get_user_name(sender.slackId)
        await reply_to_ticket(
            text=f"Hi {user_name}! Unfortunately, there is a backlog of projects awaiting ship certification; please be patient. \n\n *pssst... voting more will move your project further towards the front of the queue.*",
            ticket=ticket,
            client=env.slack_client,
        )
        await resolve(
            ts=ticket.msgTs,
            resolver=helper.slackId,
            client=env.slack_client,
        )
