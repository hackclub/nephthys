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
from prisma.models import Ticket
from prisma.models import User


macros = [Resolve, HelloWorld, FAQ, Identity, Fraud, ShipCertQueue, Thread, Reopen]


async def run_macro(
    name: str, ticket: Ticket, helper: User, macro_ts: str, text: str, **kwargs: Any
) -> bool:
    """
    Run the macro with the given name and arguments.
    """
    for macro in macros:
        if macro.name == name:
            new_kwargs = kwargs.copy()
            new_kwargs["text"] = text
            await macro().run(ticket, helper, **new_kwargs)
            await env.slack_client.chat_delete(
                channel=env.slack_help_channel, ts=macro_ts, token=env.slack_user_token
            )
            return True

    await send_heartbeat(
        f"Macro {name} not found from <@{helper.slackId}>.",
        messages=[f"Ticket ID: {ticket.id}", f"Helper ID: {helper.id}"],
    )
    return False
