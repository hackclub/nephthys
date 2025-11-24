from typing import Any

from nephthys.macros.faq import FAQ
from nephthys.macros.fraud import Fraud
from nephthys.macros.hello_world import HelloWorld
from nephthys.macros.identity import Identity
from nephthys.macros.reopen import Reopen
from nephthys.macros.resolve import Resolve
from nephthys.macros.shipcertqueue import ShipCertQueue
from nephthys.macros.thread import Thread
from nephthys.utils.env import env
from nephthys.utils.logging import send_heartbeat
from prisma.enums import TicketStatus
from prisma.models import Ticket
from prisma.models import User


macro_list = [Resolve, HelloWorld, FAQ, Identity, Fraud, ShipCertQueue, Thread, Reopen]

macros = [macro() for macro in macro_list]


async def run_macro(
    name: str, ticket: Ticket, helper: User, macro_ts: str, text: str, **kwargs: Any
) -> bool:
    """
    Run the macro with the given name and arguments.
    """
    for macro in macros:
        if name in macro.all_aliases():
            if not macro.can_run_on_closed and ticket.status == TicketStatus.CLOSED:
                return False
            new_kwargs = kwargs.copy()
            new_kwargs["text"] = text
            await macro.run(ticket, helper, **new_kwargs)
            await env.slack_client.chat_delete(
                channel=env.slack_help_channel, ts=macro_ts, token=env.slack_user_token
            )
            return True

    await env.slack_client.chat_postEphemeral(
        channel=env.slack_help_channel,
        thread_ts=ticket.msgTs,
        user=helper.slackId,
        text=f"`?{name}` is not a valid macro.",
    )
    await send_heartbeat(
        f"Macro {name} not found from <@{helper.slackId}>.",
        messages=[f"Ticket ID: {ticket.id}", f"Helper ID: {helper.id}"],
    )
    return False
