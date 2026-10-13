from nephthys.transcripts.transcript import Transcript


class Taiyaki(Transcript):
    """Transcript for Taiyaki"""

    program_name: str = "Taiyaki"
    program_owner: str = "U0943NG73PA"  # julia
    help_channel: str = "C0C82QP81DW"
    ticket_channel: str = "C0C841V89DY"
    team_channel: str = "C0AKYAHUL73"

    faq_link: str = ""
    first_ticket_create: str = """
hello! I'm fih and i'm here to help you solve your questions!
if your question has been answered, please hit the button below to mark it as resolved. ty <3!
"""
    ticket_create: str = "someone should be along to help you soon to make sure your question gets the attention it deserves. if it has been answered, please hit the button below to mark it as resolved :D"
    resolve_ticket_button: str = "resolved!"
    ticket_resolve: str = f"<@{{user_id}}> has marked this as resolved - make a new post in <#{help_channel}> if this was a mistake"

    not_allowed_channel: str = f"whoops, it looks like you're not supposed to be in that channel, pls talk to <@{program_owner}> if that's wrong"
