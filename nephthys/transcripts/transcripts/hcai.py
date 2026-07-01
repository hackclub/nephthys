from nephthys.transcripts.transcript import Transcript


class HCAI(Transcript):
    """Transcript for Hack Club AI"""

    program_name: str = "HCAI"
    program_owner: str = "U0AF7QR9J77"

    help_channel: str = "C0BDLT68ENN"
    ticket_channel: str = "C0BEF63483A"
    team_channel: str = "C0BDHH4SGDT"

    faq_link: str = "https://hackclub.enterprise.slack.com/docs/T0266FRGM/F0A7XQT5D96"
    resolve_ticket_button: str = "i get it now!"

    first_ticket_create: str = """
hi (user), it looks like this is your first time here, welcome!
someone should be along to help you soon.
if your question has been answered, please hit the button below to mark it as resolved
"""
    ticket_create: str = f"if you haven't already, check out <{faq_link}|*the FAQ*> for commonly asked questions! otherwise, someone should be here to help you soon!"
    ticket_resolve: str = f":yay: this post has been marked as resolved by <@{{user_id}}>! if you have any more questions, please make a new post in <#{help_channel}> and we'll be happy to help you out!"

    not_allowed_channel: str = f"heya, it looks like you're not supposed to be in that channel, pls talk to <@{program_owner}> if that's wrong"
    faq_macro: str = f"ooh, it looks like that question's answered in our FAQ! Have a look at <{faq_link}|*the FAQ*>"
