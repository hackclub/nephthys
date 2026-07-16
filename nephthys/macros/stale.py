from nephthys.macros.types import ReplyMacro
from nephthys.utils.env import env


class Stale(ReplyMacro):
    """
    A simple macro telling people that the ticket is stale and resolving it.
    """

    name = "stale"
    message = env.transcript.stale_tickets_macro
