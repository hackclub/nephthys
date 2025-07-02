from nephthys.actions.resolve import resolve
from nephthys.macros.types import Macro
from nephthys.utils.env import env


class FAQ(Macro):
    name = "banned"

    async def run(self, ticket, helper, **kwargs):
        """
        hopefully a simple-ish macro to inform someone that they were banned, tell them to gtfo, and close thread --neko
        """
        client = await ticket.openedBy()
        user_info = await env.slack_client.users_info(user=client.slackId)
        name = (
            user_info["user"]["profile"].get("display_name")
            or user_info["user"]["profile"].get("real_name")
            or user_info["user"]["name"]
        )
        await env.slack_client.chat_postMessage(
            text=f"hey, {name}.\nyou seem to be banned. this mean you can no longer participate in Summer of Making.\nif you are looking to appeal your ban, this is not the place for that.\nthis thread will now be closed.",
            channel=env.slack_help_channel,
            thread_ts=ticket.msgTs,
        )
        await resolve(
            ts=ticket.msgTs,
            resolver=helper.slackId,
            client=env.slack_client,
        )
