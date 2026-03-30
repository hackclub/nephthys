from prisma.models import Ticket
from prisma.models import User
from nephthys.actions.resolve import resolve
from nephthys.utils.env import env
from nephthys.utils.slack_user import get_user_profile
from nephthys.utils.ticket_methods import reply_to_ticket


class Macro:
    name: str
    aliases: list[str] = []
    can_run_on_closed: bool = False

    async def run(self, ticket: Ticket, helper: User, **kwargs) -> None:
        """
        Run the macro with the given arguments.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def all_aliases(self) -> set[str]:
        """
        Get all names for this macro, including aliases.
        """
        return set([self.name] + self.aliases)


class ReplyMacro(Macro):
    """
    A type of simple macro that follows lookup, then reply, and possibly
    resolve.

    This type of macro:
    * Looks up the sender
    * Reply to the ticket with ``message``
    * Resolve the ticket (if ``resolve_ticket``)

    Macros that have complex logic should be based on ``Macro``.
    """

    message: str
    resolve_ticket: bool = True
    can_run_on_closed = False

    async def run(self, ticket, helper, **kwargs):
        sender = await env.db.user.find_first(where={"id": ticket.openedById})
        if not sender:
            return
        user = await get_user_profile(sender.slackId)
        await reply_to_ticket(
            text=self.message.replace("(user)", user.display_name()),
            ticket=ticket,
            client=env.slack_client,
        )
        if self.resolve_ticket:
            await resolve(
                ts=ticket.msgTs,
                resolver=helper.slackId,
                client=env.slack_client,
                send_resolved_message=False,
            )
