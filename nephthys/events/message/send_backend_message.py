from slack_sdk.web.async_client import AsyncWebClient

from nephthys.utils.env import env
from prisma.models import User


async def backend_message_blocks(
    author_user_id: str,
    msg_ts: str,
    past_tickets: int,
    current_question_tag_id: int | None = None,
    reopened_by: User | None = None,
) -> list[dict]:
    thread_url = f"https://hackclub.slack.com/archives/{env.slack_help_channel}/p{msg_ts.replace('.', '')}"
    options = [
        {
            "text": {
                "type": "plain_text",
                "text": tag.label,
            },
            "value": f"{tag.id}",
        }
        for tag in await env.db.questiontag.find_many()
    ]
    initial_option = next(
        (
            option
            for option in options
            if option["value"] == f"{current_question_tag_id}"
        ),
        None,
    )
    question_tags_dropdown = {
        "type": "input",
        "label": {"type": "plain_text", "text": "Question tag", "emoji": True},
        "element": {
            "type": "static_select",
            "action_id": "question-tag-list",
            "placeholder": {
                "type": "plain_text",
                "text": "Which question tag fits?",
            },
            "options": options
            or [
                {
                    "text": {
                        "type": "plain_text",
                        "text": ":dotted_line_face: No question tags available",
                        "emoji": True,
                    },
                    "value": "None",
                }
            ],
        },
    }
    if initial_option:
        question_tags_dropdown["element"]["initial_option"] = initial_option

    return [
        question_tags_dropdown,
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "If none of the existing tags fit :point_right:",
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": ":wrench: new question tag",
                    "emoji": True,
                },
                "action_id": "create-question-tag",
            },
        },
        {
            "type": "input",
            "label": {"type": "plain_text", "text": "Team tags", "emoji": True},
            "element": {
                "action_id": "team-tag-list",
                "type": "multi_external_select",
                "placeholder": {"type": "plain_text", "text": "Select tags"},
                "min_query_length": 0,
            },
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": (
                        f"Reopened by <@{reopened_by.slackId}>. Originally submitted by <@{author_user_id}>. <{thread_url}|View thread>."
                        if reopened_by
                        else f"Submitted by <@{author_user_id}>. They have {past_tickets} past tickets. <{thread_url}|View thread>."
                    ),
                }
            ],
        },
    ]


async def send_backend_message(
    author_user_id: str,
    msg_ts: str,
    description: str,
    past_tickets: int,
    client: AsyncWebClient,
    current_question_tag_id: int | None = None,
    reopened_by: User | None = None,
    display_name: str | None = None,
    profile_pic: str | None = None,
):
    """Send a "backend" message to the tickets channel with ticket details."""

    return await client.chat_postMessage(
        channel=env.slack_ticket_channel,
        text=(
            f"Reopened ticket from <@{author_user_id}>: {description}"
            if reopened_by
            else f"New question from <@{author_user_id}>: {description}"
        ),
        blocks=await backend_message_blocks(
            author_user_id, msg_ts, past_tickets, current_question_tag_id, reopened_by
        ),
        username=display_name,
        icon_url=profile_pic,
        unfurl_links=True,
        unfurl_media=True,
    )
