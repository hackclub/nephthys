from nephthys.macros.types import ReplyMacro
from nephthys.utils.env import env


class Identity(ReplyMacro):
    """
    A simple macro telling people to use the identity help channel
    """

    name = "identity"
    message = env.transcript.identity_macro
