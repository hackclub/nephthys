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
