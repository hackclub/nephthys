from nephthys.transcripts.transcript import Transcript


class Hctg(Transcript):
    """Transcript for Hack Club The Game"""

    program_name: str = "Hack Club The Game"
    program_owner: str = "U01MPHKFZ7S"

    help_channel: str = "C0A9XULS1SL" # hctg-help
    ticket_channel: str = "C0AF2HXHNSG" # hctg-tickets
    team_channel: str = "C08B3M2DNSW" # hack-club-the-game-internals

    faq_link: str = "https://hackclub.enterprise.slack.com/docs/T0266FRGM/F0AEVK71A69"

    first_ticket_create: str = f"""
hi (user)! it looks like this is your first time here, welcome! someone should be along to help you soon but please read the <{faq_link}|faq>, it answers a lot of common questions. 
if your question has been answered, please hit the button below to mark it as resolved
"""
    ticket_create: str = f"someone should be along to help you soon but in the mean time i suggest you read the faq <{faq_link}|here> to make sure your question hasn't already been answered. if it has been, please hit the button below to mark it as resolved :D"
    resolve_ticket_button: str = "i get it now"
    ticket_resolve: str = f"oh, oh! it looks like this post has been marked as resolved by <@{{user_id}}>! if you have any more questions, please make a new post in <#{help_channel}> and someone'll be happy to help you out! not me though, i'm just a silly racoon ^-^"

    not_allowed_channel: str = f"heya, it looks like you're not supposed to be in that channel, pls talk to <@{program_owner}> if that's wrong"
