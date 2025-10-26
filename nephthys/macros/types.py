from prisma.models import Ticket
from prisma.models import User


class Macro:
    name: str
    can_run_on_closed: bool = False

    async def run(self, ticket: Ticket, helper: User, **kwargs) -> None:
        """
        Run the macro with the given arguments.
        """
        raise NotImplementedError("Subclasses must implement this method.")
