from nephthys.transcripts.transcript import Transcript


class Terra(Transcript):
    """Transcript for Terra"""

    program_name: str = "Terra"
    program_owner: str = "U07VC9705D4"  # miggy

    help_channel: str = "C0B7KLRAFFW"
    ticket_channel: str = "C0C1YG7CUJH"
    team_channel: str = "C0C1N3WCU5D"

    faq_link: str = "https://hackclub.enterprise.slack.com/docs/T0266FRGM/F0C21CF9S94"
    first_ticket_create: str = f"""
hihi! i'm poobert and i'm here to help you solve your questions! (in the meantime, please check <{faq_link}|the FAQ>)
if your question has been answered, please hit the button below to mark it as resolved. ty!
"""
    ticket_create: str = f"someone should be along to help you soon but in the meantime i suggest you read the faq <{faq_link}|here> to make sure your question hasn't already been answered. if it has been, please hit the button below to mark it as resolved :D"
    resolve_ticket_button: str = "resolved!"
    ticket_resolve: str = f"<@{{user_id}}> has marked this as resolved - make a new post in <#{help_channel}> if this was a mistake"

    not_allowed_channel: str = f"whoops, it looks like you're not supposed to be in that channel, pls talk to <@{program_owner}> if that's wrong"
