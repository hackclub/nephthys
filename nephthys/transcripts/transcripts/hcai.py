from nephthys.transcripts.transcript import Transcript


class Hcai(Transcript):
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

    max_tokens_macro: str = (
        "Try setting the max_tokens value in your request,  OpenRouter is slightly pessimistic about "
        "adhering to the daily limit - it can reject requests it thinks will go over the limit \n"
        "If you set max_tokens, OpenRouter calculates the pricing from that."
    )
    no_money_macro: str = (
        "HackClub AI is out of credits, they will be refilled soon when mahad refills them, "
        "till then they can use openrouter/free or other free models. I've closed this ticket for you"
    )
