from nephthys.macros.types import ReplyMacro
from nephthys.utils.env import env


class NoMoney(ReplyMacro):
    """
    A macro informing users that HackClub AI is out of credits.
    """

    name = "no_money"
    message = env.transcript.no_money_macro
