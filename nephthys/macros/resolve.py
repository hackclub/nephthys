from nephthys.actions.resolve import resolve
from nephthys.database.tables import Ticket
from nephthys.database.tables import TicketStatus
from nephthys.database.tables import User
from nephthys.macros.types import Macro
from nephthys.utils.env import env
from nephthys.utils.logging import send_heartbeat


class Resolve(Macro):
    name = "resolve"
    aliases = ["close"]

    async def run(self, ticket: Ticket, helper: User, **kwargs) -> None:
        """
        Resolve the ticket with the given arguments.
        """
        await send_heartbeat(
            f"Resolving ticket with ts {ticket.msg_ts} by <@{helper.slack_id}>.",
            messages=[f"Ticket ID: {ticket.id}", f"Helper ID: {helper.id}"],
        )
        if not ticket.status == TicketStatus.CLOSED:
            await resolve(
                ts=ticket.msg_ts,
                resolver=helper.slack_id,
                client=env.slack_client,
            )
        else:
            await send_heartbeat(
                f"Ticket with ts {ticket.msg_ts} is already closed. No action taken. (Trying to resolve for <@{helper.slack_id}>).",
                messages=[f"Ticket ID: {ticket.id}", f"Helper ID: {helper.id}"],
            )
            return
