from nephthys.macros.types import ReplyMacro
from nephthys.utils.env import env


class Shipwrights(ReplyMacro):
    """
    A macro used to refer people to shipwrights support.
    """
    name = "shipwrights"
    aliases = ["shipwhrights"]
    message = env.transcript.shipwrights_macro
