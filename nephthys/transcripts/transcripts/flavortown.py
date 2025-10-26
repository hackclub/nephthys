from nephthys.transcripts.transcript import Transcript


class Flavortown(Transcript):
    """Transcript for Hack Club Flavortown."""

    program_name: str = "Flavortown"
    program_owner: str = "U073M5L9U13"  # @Mish

    help_channel: str = "C09MATKQM8C"  # #flavortown-help
    ticket_channel: str = "C09LS4SAWNB"  # #flavortown-tickets
    team_channel: str = "C09M16FHL0K"  # #flavortown-support-team

    faq_link: str = "https://hackclub.slack.com/docs/T0266FRGM/F09NKF58FL5"
    identity_help_channel: str = "C092833JXKK"  # #identity-help

    first_ticket_create: str = f"""
:rac_info: Hey there (user), and welcome to the support channel! While we wait for someone to help you out, I have a couple of requests for you:
• Take a look through <{faq_link}|*the FAQ*> – you may find a solution waiting there
• Once your question has been answered, hit that green button below!
"""
    ticket_create: str = f"""
:rac_info: Ah, hello! While we wait for a human to come and help you out, I've been told to remind you to:
• Have a read of <{faq_link}|*the FAQ*> – it might have the answer you're looking for
• Once your question is answered, hit the button below!
"""
    ticket_resolve: str = f"""
Aha, this post has just been marked as resolved by <@{{user_id}}>! I'll head back to the kitchen now, \
but if you need any more help, just send another message in <#{help_channel}> and I'll be right back o/
"""

    home_unknown_user_title: str = ":upside-down_orpheus: woah, wait one sec!"
    home_unknown_user_text: str = """
_checks records_

heyy {name}, it doesn't look like you're on the list of people allowed to access this page – sorry!

If you think this isn't right, ask <@{program_owner}> and they'll check for you! I'm still new to this \
fancy "role-based access" stuff :P
"""

    not_allowed_channel: str = f"hey, it looks like you're not supposed to be in that channel, pls talk to <@{program_owner}> if that's wrong"
