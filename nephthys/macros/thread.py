from nephthys.actions.resolve import resolve
from nephthys.macros.types import Macro
from nephthys.utils.env import env


class Thread(Macro):
    name = "thread"

    async def run(self, ticket, helper, **kwargs):
        """
        A macro that deletes the Nephthys message and removes the
        reaction to avoid duplicate thread clutter
        """
        sender = await env.db.user.find_first(where={"id": ticket.openedById})
        if not sender:
            return

        # Delete the first (FAQ) message sent by the bot
        bot_info = await env.slack_client.auth_test()
        bot_user_id = bot_info.get("user_id")
        bot_messages = await env.slack_client.conversations_replies(
            channel=env.slack_help_channel,
            ts=ticket.msgTs,
        )
        for msg in bot_messages["messages"]:
            if msg["user"] == bot_user_id:
                await env.slack_client.chat_delete(
                    channel=env.slack_help_channel,
                    ts=msg["ts"],
                )

        await resolve(
            ts=ticket.msgTs,
            resolver=helper.slackId,
            client=env.slack_client,
            add_reaction=False,
            send_resolved_message=False,
        )
