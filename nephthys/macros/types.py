from nephthys.actions.resolve import resolve
from nephthys.database.tables import Ticket
from nephthys.database.tables import User
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
    * Replies to the ticket with ``message``
    * Resolves the ticket (if ``resolve_ticket``)

    Macros that have complex logic should be based on ``Macro``.
    """

    message: str
    resolve_ticket: bool = True
    can_run_on_closed = False

    async def run(self, ticket: Ticket, helper: User, **kwargs) -> None:
        # Save API calls by only fetching user if used by message
        reply_text = self.message
        if "(user)" in self.message:
            # opened_by may be a prefetched User object or a raw FK int
            sender = ticket.opened_by
            if isinstance(sender, int):
                sender = await User.objects().where(User.id == sender).first()
            if not sender:
                return
            user = await get_user_profile(sender.slack_id)
            reply_text = self.message.replace("(user)", user.display_name())

        await reply_to_ticket(
            text=reply_text,
            ticket=ticket,
            client=env.slack_client,
        )

        if self.resolve_ticket:
            await resolve(
                ts=ticket.msg_ts,
                resolver=helper.slack_id,
                client=env.slack_client,
                send_resolved_message=False,
            )
