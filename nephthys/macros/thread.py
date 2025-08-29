from nephthys.actions.resolve import resolve
from nephthys.macros.types import Macro
from nephthys.utils.env import env


class Thread(Macro):
    name = "thread"

    async def run(self, ticket, helper, **kwargs):
        """
        A simple macro telling people to use threads
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
            text=f"hey, {name}! would you mind asking your questions in the same thread? :rac_info: it helps us keep track of questions easier!\n\n(to use them, hover over the message and click :speech_balloon:)",
            channel=env.slack_help_channel,
            thread_ts=ticket.msgTs,
        )
        # Thread emoji (standard practice on Slack)
        await env.slack_client.reactions_add(
            channel=env.slack_help_channel,
            name="thread",
            timestamp=ticket.msgTs,
        )
        await resolve(
            ts=ticket.msgTs,
            resolver=helper.slackId,
            client=env.slack_client,
        )
