from nephthys.macros.types import ReplyMacro
from nephthys.utils.env import env


class Fraud(ReplyMacro):
    """
    A simple macro telling people to DM the Fraud Squad
    """

    name = "fraud"
    message = env.transcript.fraud_macro
