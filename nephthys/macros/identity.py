from nephthys.actions.resolve import resolve
from nephthys.macros.types import Macro
from nephthys.utils.env import env
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
        user_info = await env.slack_client.users_info(user=sender.slackId)
        name = (
            user_info["user"]["profile"].get("display_name")
            or user_info["user"]["profile"].get("real_name")
            or user_info["user"]["name"]
        )
        await reply_to_ticket(
            text=f"hey, {name}! please could you ask questions about identity verification in <#{env.transcript.identity_help_channel}>? :rac_cute:\n\nit helps the verification team keep track of questions easier!",
            ticket=ticket,
            client=env.slack_client,
        )
        await resolve(
            ts=ticket.msgTs,
            resolver=helper.slackId,
            client=env.slack_client,
        )
