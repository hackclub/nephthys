from nephthys.transcripts.transcript import Transcript


class Construct(Transcript):
    """Transcript for Hack Club Construct"""

    program_name: str = "Construct"
    program_owner: str = "U07H3E1CW7J"  # @Barnabás

    help_channel: str = "C09QSTUV88Y"  # #construct-help
    ticket_channel: str = "C09Q32ED8RH"  # #construct-tickets
    team_channel: str = "C09PU0RPQUX"  # #construct-support-team

    faq_link: str = "https://hackclub.slack.com/docs/T0266FRGM/F09Q2DS061J"
    identity_help_channel: str = "C092833JXKK"  # #identity-help
    first_ticket_create: str = f"""
Hey! Your support ticket is in the queue — someone from the team will pick it up soon.
While we wait:
• Try the FAQ: <{faq_link}|the FAQ> — sometimes the answer's hiding there.
• When your issue is fixed, tap the green Resolve button to close the ticket.
Thanks for the patience — we'll be with you shortly!
"""
    ticket_create: str = f"""
Hello! Your ticket has been recorded and assigned a spot in the queue.
Quick checklist:
• Check <{faq_link}|the FAQ> — it might save a step.
• If your issue gets fixed, please press the Resolve button so we know it's done.
Someone from the team will reply shortly with next steps.
"""
    ticket_resolve: str = f"""
Nice — this ticket was marked resolved by <@{{user_id}}>.
If you need additional changes or the issue returns, send a message in <#{help_channel}> and we'll take another look.
"""

    home_unknown_user_title: str = ":wrench: whoa — access limited"
    home_unknown_user_text: str = """
_Checking permissions_

Hey {name}, it looks like you don't have access to this page right now.
If that's a mistake, please ask <@{program_owner}> to grant access and include a short note about why you need it.
"""

    not_allowed_channel: str = f"Oops — you don't have permission for that channel. If you think this is wrong, ask <@{program_owner}> to check your access."
