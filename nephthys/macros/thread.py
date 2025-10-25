from nephthys.actions.resolve import resolve
from nephthys.macros.types import Macro
from nephthys.utils.env import env
from nephthys.utils.ticket_methods import delete_bot_replies


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

        # Deletes the first (FAQ) message sent by the bot
        await delete_bot_replies(ticket.id)

        await resolve(
            ts=ticket.msgTs,
            resolver=helper.slackId,
            client=env.slack_client,
            add_reaction=False,
            send_resolved_message=False,
        )
