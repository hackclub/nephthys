from nephthys.actions.resolve import resolve
from nephthys.macros.types import Macro
from nephthys.utils.env import env


class ShipCertQueue(Macro):
    name = "shipcertqueue"

    async def run(self, ticket, helper, **kwargs):
        """
        A simple macro telling people about the ship certification backlog
        """
        sender = await env.db.user.find_first(where={"id": ticket.openedById})
        if not sender:
            return
        user_info = await env.slack_client.users_info(user=sender.slackId)
        name = (
            user_info["user"]["profile"].get("display_name")
            or user_info["user"]["profile"].get("real_name")
            or user_info["user"]["name"]
        )
        await env.slack_client.chat_postMessage(
            text=f"Hi {name}! Unfortunately, there is a backlog of projects awaiting ship certification; please be patient. \n\n *pssst... voting more will move your project further towards the front of the queue.*",
            channel=env.slack_help_channel,
            thread_ts=ticket.msgTs,
        )
        await resolve(
            ts=ticket.msgTs,
            resolver=helper.slackId,
            client=env.slack_client,
        )
