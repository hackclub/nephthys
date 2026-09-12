from nephthys.transcripts.transcript import Transcript


class Atlantis(Transcript):
    """Transcript for Atlantis"""

    program_name: str = "Atlantis"
    program_owner: str = "U09AFPZ852L"  # @queso

    help_channel: str = "C0AUP8VUU6T"  # #atlantis-help
    ticket_channel: str = "C0B6PSUC3MH"  # #atlantis-tickets
    team_channel: str = "C0B6ZSDLETW"  # #atlantis-support-team

    faq_link: str = "https://hackclub.enterprise.slack.com/docs/T0266FRGM/F0BSJU62FA8"
    identity_help_channel: str = "C092833JXKK"  # #identity-help

    first_ticket_create: str = f"""
:rac_info: Hey (user), welcome to the Atlantis support channel! Someone from the community will be here to help you out soon.

If you haven't already, have a read through <{faq_link}|*the FAQ*> – it will likely contain the answer you're looking for!

_Please press "mark as resolved" once your question has been answered_
"""
    ticket_create: str = f"""
:rac_info: Hi (user), welcome back to the Atlantis support channel! Someone should be here to help you out soon.

As a reminder, you can take a look at <{faq_link}|*the FAQ*> while you wait – it might contain the answer to your question!
"""
    ticket_resolve: str = f"""
This thread has been marked as resolved by <@{{user_id}}>!

More questions? Send another message in <#{help_channel}> and we'll be there to help too!
"""

    faq_macro: str = f"""
Hi (user), this question is already answered in our FAQ!

Here's the link again: <{faq_link}|*Atlantis FAQ*>.

_I've marked this question as resolved, so please start a new thread if you need more help_
    """

    identity_macro: str = f"""
Hi (user), please could you ask questions about identity verification in <#{identity_help_channel}>?:rac_cute:

It helps the verification team keep track of questions easier!

_I've marked this thread as resolved_
"""
    fraud_macro: str = """
Hi (user), would you mind directing any fraud related queries to <@U091HC53CE8>? :rac_cute:

It'll keep your case confidential and make it easier for the fraud team to keep track of!

_I've marked this thread as resolved_
"""

    not_allowed_channel: str = f"hey, it looks like you're not supposed to be in that channel, pls talk to <@{program_owner}> if that's wrong"
