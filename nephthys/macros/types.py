from nephthys.actions.resolve import resolve
from nephthys.utils.env import env
from nephthys.utils.slack_user import get_user_profile
from nephthys.utils.ticket_methods import reply_to_ticket
from prisma.models import Ticket
from prisma.models import User


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

    message: str | None
    resolve_ticket: bool = True
    can_run_on_closed = False

    async def run(self, ticket: Ticket, helper: User, **kwargs) -> None:
        # Handle macros that may only be configured for certain events
        if not self.message:
            await env.slack_client.chat_postEphemeral(
                channel=env.slack_help_channel,
                thread_ts=ticket.msgTs,
                user=helper.slackId,
                text=f"Invalid macro: The `{self.name}` macro is not configured for this channel.",
            )
            return

        # Save API calls by only fetching user if used by message
        reply_text = self.message
        if "(user)" in self.message:
            # Try pre-fetched relation first
            sender = getattr(ticket, "openedBy", None)
            if sender is None and getattr(ticket, "openedById", None) is not None:
                sender = await env.db.user.find_first(where={"id": ticket.openedById})
            if not sender:
                return
            user = await get_user_profile(sender.slackId)
            reply_text = self.message.replace("(user)", user.display_name())

        await reply_to_ticket(
            text=reply_text,
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
