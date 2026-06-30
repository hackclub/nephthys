from nephthys.transcripts.transcript import Transcript


class Outpost(Transcript):
    """Transcript for Outpost"""

    program_name: str = "outpost"
    program_owner: str = "U08TCSANHDX"

    help_channel: str = "C0BDYK5QQEM"
    ticket_channel: str = "C0BCQJLCYDD"
    team_channel: str = "C0BD9MB5FJ8"

    faq_link: str = "https://hack.af/outpost-info"
    identity_help_channel: str = "C092833JXKK"

    first_ticket_create: str = f"""
heya (user)! welcome to outpost! an outpost team member will come by to help you soon but please read the <{faq_link}|faq> for answers to common questions. 
if your question has been answered, please hit the button below to mark it as resolved
"""
    ticket_create: str = f"an outpost team member will be with you asap, in the mean time please read the faq <{faq_link}|here> to make sure your question hasn't already been answered. if it has been, please hit the button below to mark it as resolved :3"
    resolve_ticket_button: str = "resolve ticket :3"
    ticket_resolve: str = f"wow! this post has been marked as resolved by <@{{user_id}}>! if you have any more questions, please make a new post in <#{help_channel}> and an outpost team member will be happy to help you out! :p"

    not_allowed_channel: str = f"heya, it looks like you're not supposed to be in that channel, pls talk to <@{program_owner}> if that's wrong"
