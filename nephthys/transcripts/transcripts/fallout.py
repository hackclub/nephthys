from nephthys.transcripts.transcript import Transcript


class Fallout(Transcript):
    """Transcript for Hack Club Fallout"""

    program_name: str = "fallout"
    program_owner: str = "U03UBRVG2MS"  # @samliu

    help_channel: str = "C0ACJ290090"  # fallout-help
    ticket_channel: str = "C0ACS0H0RGU"  # fallout-tickets
    team_channel: str = "C0A8XFSR5LH"  # fallout-bts

    faq_link: str = "https://hackclub.enterprise.slack.com/docs/T0266FRGM/F0ACBK8L8GK"
    identity_help_channel: str = "C092833JXKK"  # identity-help
    fallout_channel: str = "C037157AL30"  # fallout

    first_ticket_create: str = f"""
:oi: oi, (user). welcome to the support channel! someone from the team's going to help you soon, please be patient!

while we wait, here's what i need to tell you:
• carefully read through our <{faq_link}|*FAQ*> – your question might already be answered!
• be patient! we respond slower outside business hours (weekdays 9am - 5pm eastern) and on US holidays.
• if you have questions about your project, like how to use a component, or wire it, ask in <#{fallout_channel}> instead.
• once your question has been answered, hit that green button below!
"""
    ticket_create: str = f"""
:oi: hi again! i'm here to remind you of a few things while you wait:
• carefully read through our <{faq_link}|*FAQ*> – your question might already be answered!
• be patient! we respond slower outside business hours (weekdays 9am - 5pm eastern) and on US holidays.
• reviews take time, asking here won't speed it up. make sure your project meets all requirements before submitting!
• if you have questions about your project, like how to use a component, or wire it, ask in <#{fallout_channel}> instead.
• once your question has been answered, hit that green button below!
"""
    ticket_resolve: str = f"""
oh! it looks like this has been marked as resolved by <@{{user_id}}>. i'm out! \
if you need any more help, just send another message in <#{help_channel}>!
"""

    faq_macro: str = f"""
    hey (user), this question is already answered in our FAQ! in case you missed it, you can get it here: <{faq_link}|*Fallout FAQ*>.

    _i've marked this as resolved. if you need any more help, just send another message in <#{help_channel}>!_
    """

    not_allowed_channel: str = f"hey, it looks like you're not supposed to be in that channel, pls talk to <@{program_owner}> if that's wrong"
