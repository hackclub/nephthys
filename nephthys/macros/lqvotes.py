from nephthys.actions.resolve import resolve
from nephthys.macros.types import Macro
from nephthys.utils.env import env
from nephthys.utils.slack_user import get_user_profile
from nephthys.utils.ticket_methods import reply_to_ticket


class LQVotes(Macro):
    name = "lqvote"
    aliases = ["lqvote", "lqvotes"]

    async def run(self, ticket, helper, **kwargs):
        """
        Macro to warn users their votes are being marked low-quality.
        """
        macro_text = env.transcript.lqvotes_macro
        if not macro_text:
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
