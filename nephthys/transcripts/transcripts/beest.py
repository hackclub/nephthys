from nephthys.transcripts.transcript import Transcript


class Beest(Transcript):
    """Transcript for beest-help"""

    program_name: str = "beest"
    program_owner: str = "U06T30DNB3L"

    help_channel: str = "C0AQ4T1CWH2"
    ticket_channel: str = "C0AV9GE0PA5"
    team_channel: str = "C0APP5ZMWUQ"

    faq_link: str = "https://beest.hackclub.com/FAQ"
 
    first_ticket_create: str = f"""
Heya! Im an automation that assigns helpers to your question! First off, have you read the <{faq_link}|faq>, it answers a lot of common questions!
if your question has been answered, please hit the button below to mark it as resolved
"""
    ticket_create: str = f"someone should be along to help you soon but in the mean time i suggest you read the faq <{faq_link}|here> to make sure your question hasn't already been answered. if it has been, please hit the button below to mark it as resolved :D"
    resolve_ticket_button: str = "i get it now"
    ticket_resolve: str = f"<@{{user_id}}> Has marked this as resolved - make a new post in <#{help_channel}> if this was a mistake"

    not_allowed_channel: str = f"heya, it looks like you're not supposed to be in that channel, pls talk to <@{program_owner}> if that's wrong"
