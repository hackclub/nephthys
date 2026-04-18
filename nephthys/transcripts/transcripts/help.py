from nephthys.transcripts.transcript import Transcript


class Help(Transcript):
    """Transcript for help"""

    program_name: str = "help"
    program_owner: str = "U07F6FMJ97U"

    help_channel: str = "C07TM4C0AQ5"  # help
    ticket_channel: str = "C0AS7CGTK8W"  # help-ticket
    team_channel: str = "C0APKHZG495"  # help-channel-bts

    faq_link: str = "https://hackclub.enterprise.slack.com/docs/T0266FRGM/F0AR3EQK621"

    first_ticket_create: str = f"""
hi (user)! seems like it's your first time, welcome to the help channel! someone will be here soon to help answer your question! for now, feel free to look at the <{faq_link}|faq>, it answers some common questions and gives basic information. 
if your question has been answered, please hit the button below to mark it as resolved ^-^
"""
    ticket_create: str = f"someone will be here soon to help answer your question! for now, feel free to look at the <{faq_link}|faq>, it answers some common questions and gives basic information. if your question has been answered, please hit the button below to mark it as resolved ^-^"
    resolve_ticket_button: str = "i get it now"
    ticket_resolve: str = f"oh, oh! it looks like this post has been marked as resolved by <@{{user_id}}>! if you have any more questions, please make a new post in <#{help_channel}> and someone'll be happy to help you out! not me though, i'm just a silly racoon ^-^"

    not_allowed_channel: str = f"heyo! doesn't seem like you're supposed to be in that channel, please reach out to <@{program_owner}> if that's wrong!"
