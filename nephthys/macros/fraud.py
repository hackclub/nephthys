from nephthys.actions.resolve import resolve
from nephthys.macros.types import Macro
from nephthys.utils.env import env


class Fraud(Macro):
    name = "fraud"

    async def run(self, ticket, helper, **kwargs):
        """
        A simple macro telling people to use Fraudpheus
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
            text=f"Hiya {name}! Would you mind directing any fraud related queries to <@U091HC53CE8>? :rac_cute:\n\nIt'll keep your case confidential and make it easier for the fraud team to keep track of!",
            channel=env.slack_help_channel,
            thread_ts=ticket.msgTs,
        )
        await resolve(
            ts=ticket.msgTs,
            resolver=helper.slackId,
            client=env.slack_client,
        )
