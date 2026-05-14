from nephthys.transcripts.transcript import Transcript


class StardanceAmbassadors(Transcript):
    """Transcript for Hack Club Stardance Ambassadors."""

    program_name: str = "Stardance Ambassadors"
    program_owner: str = "U093AJCBP0C"  # @Alfie

    help_channel: str = "C0AS0FD28RE"  
    ticket_channel: str = "C0ATNQYMRJS"  
    team_channel: str = "C0AQC0W6BQS" 

    faq_link: str = "https://hackclub.enterprise.slack.com/docs/T0266FRGM/F0AR6B599NW"
    identity_help_channel: str = "C092833JXKK"  # #identity-help

    first_ticket_create: str = f"""
:ambassador: Hey there {user}! While we wait for someone to help you, please:
• take a look through <{faq_link}|*the handbook*> - you may find the answer to your question there
• once your question has been answered, hit that green button below!
"""
    ticket_create: str = f"""
:ambassador: Hey there {user}! While we wait for someone to help you, please:
• take a look through <{faq_link}|*the handbook*> - you may find the answer to your question there
• once your question has been answered, hit that green button below!
"""
    ticket_resolve: str = f"""
:ambassador-thumbsup:, this post has just been marked as resolved by <@{{user_id}}>! If you need any more help just send another message in <#{help_channel}>!
"""

    not_allowed_channel: str = f"hey, it looks like you're not supposed to be in that channel, pls talk to <@{program_owner}> if that's wrong"
