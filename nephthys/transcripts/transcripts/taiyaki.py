from nephthys.transcripts.transcript import Transcript


class Taiyaki(Transcript):
    """Transcript for Taiyaki"""

    program_name: str = "Taiyaki"
    program_owner: str = "U0943NG73PA"  # julia
    help_channel: str = "C0C82QP81DW"
    ticket_channel: str = "C0C841V89DY"
    team_channel: str = "C0AKYAHUL73"

    faq_link: str = "https://hackclub.enterprise.slack.com/docs/T0266FRGM/F0C712C3SR5"
    identity_help_channel: str = "C092833JXKK"

    first_ticket_create: str = f"""
hello! I'm fih and i'm here to help you solve your questions!
while you wait, take a peek at the <{faq_link}|faq> - it might already have your answer!
if your question has been answered, please hit the button below to mark it as resolved. ty <3!
"""
    ticket_create: str = f"someone should be along to help you soon to make sure your question gets the attention it deserves. while you wait, take a peek at the <{faq_link}|faq> - it might already have your answer! if it has been answered, please hit the button below to mark it as resolved :D"
    resolve_ticket_button: str = "resolved!"
    ticket_resolve: str = f"<@{{user_id}}> has marked this as resolved - make a new post in <#{help_channel}> if this was a mistake"
    ticket_resolve_stale: str = f"it looks like this post is a bit old! if you still need help, please make a new post in <#{help_channel}> and someone'll be happy to help you out :fish:"

    faq_macro: str = f"hey, (user)! this question is answered in the faq i sent earlier, please make sure to check it out! :fish:\n\n<{faq_link}|here it is again>"
    identity_macro: str = f"hey, (user)! please could you ask questions about identity verification in <#{identity_help_channel}>? :fish:\n\nit helps the verification team keep track of questions easier!"
    fraud_macro: str = "hiya (user)! would you mind directing any fraud related queries to <@U091HC53CE8>? :fish:\n\nit'll keep your case confidential and make it easier for the fraud team to keep track of!"
    hackatime_macro: str = "hi (user), could you send that question to the Hackatime team at https://letterbird.co/hackatime? :fish:\n\nthey'll be able to provide better help for Hackatime-specific issues!\n\n_i've marked this thread as resolved_"

    not_allowed_channel: str = f"whoops, it looks like you're not supposed to be in that channel, pls talk to <@{program_owner}> if that's wrong"
