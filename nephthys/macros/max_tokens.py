from nephthys.macros.types import ReplyMacro
from nephthys.utils.env import env


class MaxTokens(ReplyMacro):
    """
    A macro for explaining how to fix insufficient credits errors.
    """

    name = "max_tokens"
    message = env.transcript.max_tokens_macro
    resolve_ticket = False
