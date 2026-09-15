from nephthys.transcripts.transcript import Transcript


class Capitol(Transcript):
    """Transcript for Capitol."""

    program_name: str = "Capitol"
    program_owner: str = "U0BCQD74Y03" # archer
    help_channel: str = "C0BT42D77U5"
    ticket_channel: str = "C0C1JPL8K6X"
    team_channel: str = "C0C1P2R1LTY"

    first_ticket_create: str = """
oh, hey (user) it looks like this is your first time here, welcome! someone should be along to help you soon.
if your question has been answered, please hit the button below to mark it as resolved
"""
    ticket_create: str = "someone should be along to help you soon, once your question is resolved please hit the button below to mark it as resolved :D"
    ticket_resolve: str = f"oh, oh! it looks like this post has been marked as resolved by <@{{user_id}}>! if you have any more questions, please make a new post in <#{help_channel}> and someone'll be happy to help you out! not me though, i'm just a silly raccoon ^-^"

    not_allowed_channel: str = f"heya, it looks like you're not supposed to be in that channel, pls talk to <@{program_owner}> if that's wrong"
