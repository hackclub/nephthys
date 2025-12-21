from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.utils.env import env
from nephthys.utils.logging import send_heartbeat
from nephthys.views.modals.create_question_tag import get_create_question_tag_modal


async def create_question_tag_view_callback(
    ack: AsyncAck, body: dict, client: AsyncWebClient
):
    """
    Callback for the create question tag view submission
    """
    await ack()
    user_id = body["user"]["id"]

    user = await env.db.user.find_unique(where={"slackId": user_id})
    if not user or not user.helper:
        await send_heartbeat(
            f"Attempted to create question tag by non-helper <@{user_id}>"
        )
        return

    label = body["view"]["state"]["values"]["tag_label"]["tag_label"]["value"]
    await env.db.questiontag.create(data={"label": label})

    # await open_app_home("question-tags", client, user_id)


async def create_question_tag_btn_callback(
    ack: AsyncAck, body: dict, client: AsyncWebClient
):
    """
    Open modal to create a question tag
    """
    await ack()
    user_id = body["user"]["id"]
    trigger_id = body["trigger_id"]

    user = await env.db.user.find_unique(where={"slackId": user_id})
    if not user or not user.helper:
        await send_heartbeat(
            f"Attempted to open create-question-tag modal by non-helper <@{user_id}>"
        )
        return

    view = get_create_question_tag_modal()
    await client.views_open(trigger_id=trigger_id, view=view, user_id=user_id)
