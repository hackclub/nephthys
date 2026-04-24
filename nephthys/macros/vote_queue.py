from nephthys.macros.types import ReplyMacro
from nephthys.utils.env import env


class VoteQueue(ReplyMacro):
    name = "votequeue"
    aliases = ["voteq"]
    message = env.transcript.vote_queue_macro
