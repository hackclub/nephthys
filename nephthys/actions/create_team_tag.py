from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.database.tables import TeamTag
from nephthys.database.tables import User
from nephthys.events.app_home_opened import open_app_home
from nephthys.utils.logging import send_heartbeat
from nephthys.views.modals.create_team_tag import get_create_team_tag_modal


async def create_team_tag_view_callback(
    ack: AsyncAck, body: dict, client: AsyncWebClient
):
    """
    Callback for the create tag view submission
    """
    await ack()
    user_id = body["user"]["id"]

    user = await User.objects().where(User.slack_id == user_id).first()
    if not user or not user.admin:
        await send_heartbeat(f"Attempted to create tag by non-admin user <@{user_id}>")
        return

    name = body["view"]["state"]["values"]["tag_name"]["tag_name"]["value"]
    tag = TeamTag(name=name)
    await tag.save()

    await open_app_home("team-tags", client, user_id)


async def create_team_tag_btn_callback(
    ack: AsyncAck, body: dict, client: AsyncWebClient
):
    """
    Open modal to create a tag
    """
    await ack()
    user_id = body["user"]["id"]
    trigger_id = body["trigger_id"]

    user = await User.objects().where(User.slack_id == user_id).first()
    if not user or not user.admin:
        await send_heartbeat(
            f"Attempted to open create tag modal by non-admin user <@{user_id}>"
        )
        return

    view = get_create_team_tag_modal()
    await client.views_open(trigger_id=trigger_id, view=view, user_id=user_id)
