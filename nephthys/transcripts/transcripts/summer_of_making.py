from nephthys.transcripts.transcript import Transcript
from nephthys.utils.env import env


class SummerOfMaking(Transcript):
    """Transcript for Summer of Making program."""

    program_name: str = "Summer of Making"

    faq_link: str = "https://hackclub.slack.com/docs/T0266FRGM/F090MQF0H2Q"
    summer_help_channel: str = "C091D312J85"
    identity_help_channel: str = "C092833JXKK"

    first_ticket_create: str = f"""
oh, hey (user) it looks like this is your first time here, welcome! someone should be along to help you soon but in the mean time i suggest you read the faq <{faq_link}|here>, it answers a lot of common questions. 
if your question has been answered, please hit the button below to mark it as resolved
"""
    ticket_create: str = f"someone should be along to help you soon but in the mean time i suggest you read the faq <{faq_link}|here> to make sure your question hasn't already been answered. if it has been, please hit the button below to mark it as resolved :D"
    ticket_resolve: str = f"oh, oh! it looks like this post has been marked as resolved by <@{{user_id}}>! if you have any more questions, please make a new post in <#{env.slack_help_channel}> and someone'll be happy to help you out! not me though, i'm just a silly racoon ^-^"

    home_unknown_user_title: str = (
        ":upside-down_orpheus: woah, stop right there {name}!"
    )
    home_unknown_user_text: str = f"oh, oh! it looks like this post has been marked as resolved by <@{{user_id}}>! if you have any more questions, please make a new post in <#{env.slack_help_channel}> and someone'll be happy to help you out! not me though, i'm just a silly racoon ^-^"

    not_allowed_channel: str = f"heya, it looks like you're not supposed to be in that channel, pls talk to <@{env.slack_maintainer_id}> if that's wrong"

    dm_magic_link_no_user: str = (
        ":rac_cute: heya, please provide the user you want me to dm"
    )
    dm_magic_link_error = f":rac_nooo: something went wrong while generating the magic link, please bug <@{env.slack_maintainer_id}> (status: {{status}})"

    dm_magic_link_success = (
        ":rac_cute: magic link sent! tell em to check their dms with me :D"
    )

    dm_magic_link_message = ":rac_cute: hey there! i got told that you got a bit stuck so here's a magic link for ya :D\n{magic_link}"

    dm_magic_link_no_permission = f":rac_nooo: you don't have permission to use this command, please bug <@{env.slack_maintainer_id}> if you think this is a mistake"
