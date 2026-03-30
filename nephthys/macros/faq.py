from nephthys.macros.types import ReplyMacro
from nephthys.utils.env import env


class FAQ(ReplyMacro):
    """
    A simple macro reminding people to check the FAQ.
    """

    name = "faq"
    message = env.transcript.faq_macro
