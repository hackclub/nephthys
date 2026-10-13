from nephthys.transcripts.transcript import Transcript

DETAIL_GUIDANCE = "Please ensure you're providing as much detail as possible. For linking to Attend users, please send the participant's admin page path, e.g. `/admin/events/haven-jollyland/participants/ATTENDEE_ID`"


class AttendHaven(Transcript):
    """Transcript for Attend (Haven support)."""

    program_name: str = "Attend Haven"
    program_owner: str = "U07BLJ1MBEE"
    help_channel: str = "C0C8FDYLNR3"
    ticket_channel: str = "C0C85BUUELX"
    team_channel: str = "C0C8LHVE11Q"
    faq_link: str = "https://attend.hackclub.com/docs"

    first_ticket_create: str = f"""
Hi (user). Looks like this is your first time here, welcome! A member of the Attend team should be along to help you as soon as possible.
If your question has been answered, please hit the button below to mark it as resolved.
{DETAIL_GUIDANCE}
"""
    ticket_create: str = f"Hi (user). Someone should be along to help you soon, once your question is resolved please hit the button below to mark it as resolved. {DETAIL_GUIDANCE}"
    ticket_resolve: str = f"It looks like this post has been marked as resolved by <@{{user_id}}>! If you need any further help, please make a new post in <#{help_channel}> and someone'll be happy to help you out!"
    ticket_resolve_stale: str = f"It looks like this post is a bit old! If you still need help, please make a new post in <#{help_channel}> and someone'll be happy to help you out!"
    ticket_reopen: str = "It looks like <@{helper_slack_id}> has reopened this post! One of the Attend team will be with you shortly."
    thread_broadcast_delete: str = "Hi there. Please ensure you're threading your messages to ensure the Attend team is able to get to all of your support queries."
    faq_macro: str = f"Hi (user)! This question is covered in the Attend docs, please check them out: <{faq_link}|attend.hackclub.com/docs>"
