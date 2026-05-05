from nephthys.actions.reopen import reopen
from nephthys.database.enums import TicketStatus
from nephthys.macros.types import Macro
from nephthys.utils.env import env


class Reopen(Macro):
    name = "reopen"
    aliases = ["unresolve", "open"]
    can_run_on_closed = True

    async def run(self, ticket, helper, **kwargs):
        """
        A simple macro to reopen a closed ticket
        """
        if ticket.status != TicketStatus.CLOSED:
            await env.slack_client.chat_postEphemeral(
                channel=env.slack_help_channel,
                thread_ts=ticket.msg_ts,
                user=helper.slack_id,
                text="Cannot reopen — this ticket isn't resolved!",
            )
            return

        await reopen(ticket, helper, env.slack_client)
