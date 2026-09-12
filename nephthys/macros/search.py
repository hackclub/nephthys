from nephthys.macros.types import ReplyMacro
from nephthys.utils.env import env


class Search(ReplyMacro):
    """
    A macro recommending the Exa API for search as search.hackclub.com is deprecated.
    """

    name = "search"
    message = env.transcript.search_macro
