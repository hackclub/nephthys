from nephthys.transcripts.transcript import Transcript


class Shredder(Transcript):
    """Transcript for Shredder"""

    program_name: str = "Shredder"         
    program_owner: str = "U06U1CBK589"          

    help_channel: str = "C0CFX3T2JJJ"              # #shredder-help
    ticket_channel: str = "C0C633F4ZMG"            # #shredder-tickets
    team_channel: str = "C0CFSL8HU91"              # #shredder-help-bts

    faq_link: str = "https://shredder.hackclub.com/faq"           # Shredder FAQ

    first_ticket_create: str = f"""
hey (user), welcome to shredder help! someone will be along soon. in the meantime, the <{faq_link}|faq> might already have your answer.
if your question's been answered, hit the button below to mark it as resolved!
"""
    ticket_create: str = f"someone will be along soon! meanwhile, check the <{faq_link}|faq> in case it's already answered. if it is, hit the button below to mark it resolved :D"
    resolve_ticket_button: str = "solved!"
    ticket_resolve: str = f"<@{{user_id}}> marked this as resolved! got another question? make a new post in <#{help_channel}>"

    not_allowed_channel: str = f"whoops, looks like you're not supposed to be in that channel, talk to <@{program_owner}> if that's wrong"