from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.utils.env import env
from nephthys.utils.logging import send_heartbeat
from nephthys.views.modals.create_category_tag import get_create_category_tag_modal


async def create_category_tag_view_callback(
    ack: AsyncAck, body: dict, client: AsyncWebClient
):
    """
    Callback for the create category tag view submission
    """
    await ack()
    user_id = body["user"]["id"]

    user = await env.db.user.find_unique(where={"slackId": user_id})
    if not user or not user.helper:
        await send_heartbeat(
            f"Attempted to create category tag by non-helper <@{user_id}>"
        )
        return

    name = body["view"]["state"]["values"]["tag_name"]["tag_name"]["value"]
    await env.db.categorytag.create(
        data={"name": name, "createdBy": {"connect": {"id": user.id}}}
    )

    # await open_app_home("question-tags", client, user_id)


async def create_category_tag_btn_callback(
    ack: AsyncAck, body: dict, client: AsyncWebClient
):
    """
    Open modal to create a category tag
    """
    await ack()
    user_id = body["user"]["id"]
    trigger_id = body["trigger_id"]

    user = await env.db.user.find_unique(where={"slackId": user_id})
    if not user or not user.helper:
        await send_heartbeat(
            f"Attempted to open create-category-tag modal by non-helper <@{user_id}>"
        )
        return

    view = get_create_category_tag_modal()
    await client.views_open(trigger_id=trigger_id, view=view, user_id=user_id)
