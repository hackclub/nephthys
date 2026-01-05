from nephthys.transcripts.transcript import Transcript


class Jumpstart(Transcript):
    """Transcript for Hack Club Jumpstart"""

    program_name: str = "Jumpstart"
    program_owner: str = "U06UYA4AH6F"  # @ Magic Frog

    help_channel: str = "C0A620A4FGF"  # #jumpstart-help
    ticket_channel: str = "C0A7CCXC8AU"  # #jumpstart-tickets
    team_channel: str = "C0A6ELTS38V"  # #jumpstart-support-team

    faq_link: str = "https://hackclub.enterprise.slack.com/docs/T0266FRGM/F0A6AMXU744"
    identity_help_channel: str = "C092833JXKK"  # #identity-help

    first_ticket_create: str = f"""
:godot: Hey (user)! I'm Godorpheus, your friendly game-dev sidekick.  
While a human helper gets to your question, you can:  
• Check out <{faq_link}|*the FAQ*> — it might already have the answer you need  
• When your question is solved, hit the green button below so I can level up my helpfulness!
"""
    ticket_create: str = f"""
:rac_info: Hey (user)! Godorpheus here — just hanging out in code-space while we wait for a human helper.  
• Take a peek at <{faq_link}|*the FAQ*> — it might already contain the answer you’re looking for  
•Once your question is resolved, tap the green button below to complete this quest 🏁
"""
    ticket_resolve: str = f"""
✅ This post has been marked as resolved by <@{{user_id}}>! I’m heading back to my digital corner.  
Need more help? Post in <#{help_channel}> and I’ll respawn instantly!
"""

    faq_macro: str = f"""
Hey (user)! This question’s already answered in the FAQ: <{faq_link}|*Jumpstart FAQ*> 🎮  

_I’ve marked this thread as resolved. Start a new thread if you need more help!_
"""
    identity_macro: str = f"""
Hey (user)! For identity verification questions, please head over to <#{identity_help_channel}> :rac_cute:  

It keeps things tidy and makes it easier for the verification team to help.  

_I’ve marked this thread as resolved!_
"""
    fraud_macro: str = """
Hey (user)! Fraud-related questions go to <@U08TU92QGHM> — they handle it all securely 🛡️  

_I’ve marked this thread as resolved to keep things organized!_
"""

    not_allowed_channel: str = f"hey, it looks like you're not supposed to be in that channel, pls talk to <@{program_owner}> if that's wrong"
