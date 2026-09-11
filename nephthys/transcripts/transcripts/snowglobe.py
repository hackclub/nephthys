from nephthys.transcripts.transcript import Transcript


class Snowglobe(Transcript):
    """Transcript for snowgloooobe"""

    program_name: str = "Snowglobe"
    program_owner: str = "U078JCFHQ3D"

    help_channel: str = "C0BNGEZR0P9"
    ticket_channel: str = "C0C114P9S03"
    team_channel: str = "C0BPMAXQTTN"

    faq_link: str = "https://snowglobe.hackclub.com/faq"
    first_ticket_create: str = f"""
hello! i am a bot with a name strikingly similar to hack club's founder, zach latta, and i'm here to solve your questions! psst: you might find an answer at <{faq_link}|the FAQ> :)
if your question has been answered, please hit the button below to mark it as resolved. ty!
"""
    ticket_create: str = f"someone should be along to help you soon but in the meantime i suggest you read the faq <{faq_link}|here> to make sure your question hasn't already been answered. if it has been, please hit the button below to mark it as resolved :D"
    resolve_ticket_button: str = "solved!"
    ticket_resolve: str = f"<@{{user_id}}> has marked this as resolved - make a new post in <#{help_channel}> if this was a mistake"

    not_allowed_channel: str = f"whoops, it looks like you're not supposed to be in that channel, pls talk to <@{program_owner}> if that's wrong"
