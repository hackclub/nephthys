from nephthys.transcripts.transcript import Transcript


class Midnight(Transcript):
    """Transcript for Hack Club Midnight."""

    program_name: str = "Midnight"
    program_owner: str = "U07BLJ1MBEE"  # @Leo

    help_channel: str = "C09Q8DY9738"  # #midnight-help
    ticket_channel: str = "C09Q0EA66H5"  # #midnight-tickets
    team_channel: str = "C09KN7YLPA5"  # #hq-midnight

    faq_link: str = "https://hackclub.slack.com/docs/T0266FRGM/F09Q464T9LK"
    identity_help_channel: str = "C092833JXKK"  # #identity-help

    first_ticket_create: str = f"""
:midnight-crow: Why hello there (user), and welcome to the Midnight support channel! While we wait for someone to help you out, I have a couple of requests for you:
• take a look through <{faq_link}|*the FAQ*> - you may find a solution waiting there
• once your question has been answered, hit that cute lil green button below!
"""
    ticket_create: str = f"""
:midnight-crow: Ah, hello! While we wait for a human to come and help you out, I've been told to remind you to:
• have a read of <{faq_link}|*the FAQ*> - it might have the answer you're looking for
• once your question is answered, hit the cute lil green button below!
"""
    ticket_resolve: str = f"""
Aha, this post has just been marked as resolved by <@{{user_id}}>! I'll head back to my castle now, \
but if you need any more help, just send another message in <#{help_channel}> and I'll be right back o/
"""

    not_allowed_channel: str = f"hey, it looks like you're not supposed to be in that channel, pls talk to <@{program_owner}> if that's wrong"
