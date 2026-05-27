from nephthys.transcripts.transcript import Transcript


class Stardance(Transcript):
    """Transcript for Stardance Challenge"""

    program_name: str = "Stardance"
    program_owner: str = "U073M5L9U13"  # @Mish

    help_channel: str = "C0AP0NMSP3P"  # #stardance-help
    ticket_channel: str = "C0B2KKWCMRN"  # #stardance-tickets
    team_channel: str = "C0B1K0L1327"  # #stardance-support-scouts

    # faq_link: str = "https://hackclub.slack.com/docs/T0266FRGM/F09NKF58FL5"
    identity_help_channel: str = "C092833JXKK"  # #identity-help

    first_ticket_create: str = """
:rac_info: Hey (user), welcome to the Stardance Challenge support channel! Someone from the community will be here to help you out soon.

_Please press "mark as resolved" once your question has been answered_
"""
    ticket_create: str = """
:rac_info: Hi (user), welcome back to the Stardance support channel! Someone should be here to help you out soon.
"""
    ticket_resolve: str = f"""
This thread has been marked as resolved by <@{{user_id}}>!

• If you have another question, send another message in <#{help_channel}> and someone will help you out! (Not me though - I'm just a silly raccoon)
• If this thread was resolved by mistake, just hit "Reopen" below!
"""

    #     faq_macro: str = f"""
    # Hi (user), this question is already answered in our FAQ! Here's the link again: <{faq_link}|*Flavortown FAQ*>.

    # _I've marked this question as resolved, so please start a new thread if you need more help_
    # """
    identity_macro: str = f"""
Hi (user), please could you ask questions about identity verification in <#{identity_help_channel}>? :rac_cute:

It helps the verification team keep track of questions easier!

_I've marked this thread as resolved_
"""
    fraud_macro: str = """
Hi (user), would you mind directing any fraud related queries to <@U091HC53CE8>? :rac_cute:

It'll keep your case confidential and make it easier for the fraud team to keep track of!

_I've marked this thread as resolved_
"""

    not_allowed_channel: str = f"hey, it looks like you're not supposed to be in that channel, pls talk to <@{program_owner}> if that's wrong"

    vote_quality_macro: str | None = """
Hi! Poor-quality votes are likely to get rejected by the platform, which means they won't count towards your vote balance. Good voters do the following:

• Look at the demo and repository links
• Look through the devlogs
• Give accurate, thoughtful scores
• Write genuine and personal feedback
"""
