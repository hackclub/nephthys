from nephthys.macros.types import ReplyMacro
from nephthys.utils.env import env


class VoteQuality(ReplyMacro):
    name = "votequality"
    aliases = ["lqvotes"]
    message = env.transcript.vote_quality_macro
