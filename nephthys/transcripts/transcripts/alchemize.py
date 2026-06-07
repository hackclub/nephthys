from nephthys.transcripts.transcript import Transcript

class Alchemize(Transcript):
    """Transcript for Alchemize YSWS"""

    program_name: str = "Alchemize"
    program_owner: str = "U096RMRG03G" # @coolcream also @aoishik(U0A5NKH93BJ)

    help_channel: str = "C0ASVK0HHEX" #alchemize-help
    ticket_channel: str = "C0B22UW9FLG"
    team_channel: str = "C0AU2U67G0P"

    faq_link: str = "https://hackclub.enterprise.slack.com/docs/T0266FRGM/F0ASVGKKBRD"
    first_ticket_create: str = """
Heya (user)! Welcome to the Alchemize support channel! Someone from our team will be here to help you out soon.
If you haven't already, have a read through <{faq_link}|*the FAQ*> – it will likely contain the answer you're looking for!
If your question has been answered, please hit the button below to mark it as resolved!
    """
    ticket_create: str = """
Hi (user), welcome back to the Alchemize support channel! Someone should be along to help you soon.
As a reminder, you can take a look at <{faq_link}|*the FAQ*> while you wait – it might contain the answer to your question! :D
"""
    resolve_ticket_button: str = "Mark As Resolved"
    ticket_resolve: str = f"<@{{user_id}}> has marked this as resolved. Feel free to make a new post in <#{help_channel}>, if you think this was a mistake, you may reopen this ticket. More questions? Send another message in <#{help_channel}> and we'll be there to help too!"

    not_allowed_channel: str = f"Heya, it looks like you're not supposed to be in that channel, pls talk to <@{program_owner}> If that's wrong."
    faq_macro: str = f"""
Hi (user), this question is already answered in our FAQ!

Here's the link again: <{faq_link}|*Alchemize FAQ*>.

_I've marked this question as resolved, so please start a new thread if you need more help_
    """
