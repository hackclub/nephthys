import logging

from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.utils.env import env
from nephthys.utils.logging import send_heartbeat
from nephthys.views.modals.edit_team_tag import get_edit_team_tag_modal


async def edit_team_tag_btn_callback(
    ack: AsyncAck, body: dict, client: AsyncWebClient
):
    await ack()
    user_id = body["user"]["id"]
    trigger_id = body["trigger_id"]
    tag_id = int(body["actions"][0]["value"])

    user = await env.db.user.find_unique(where={"slackId": user_id})
    if not user or not user.admin:
        await send_heartbeat(
            f"Attempted to open edit team tag modal by non-admin user <@{user_id}>"
        )
        return

    tag = await env.db.tag.find_unique(where={"id": tag_id})
    if not tag:
        logging.error(f"Team tag not found: id={tag_id}")
        return

    view = get_edit_team_tag_modal(tag.id, tag.name, tag.description)
    await client.views_open(trigger_id=trigger_id, view=view, user_id=user_id)


async def edit_team_tag_view_callback(
    ack: AsyncAck, body: dict, client: AsyncWebClient
):
    await ack()
    user_id = body["user"]["id"]
    callback_id = body["view"]["callback_id"]
    tag_id = int(callback_id.replace("edit_team_tag_", ""))
    values = body["view"]["state"]["values"]

    name = values["tag_name"]["tag_name"]["value"]

    raw_description = values["tag_description"]["tag_description"]["value"]
    description = raw_description.strip() if raw_description else None

    user = await env.db.user.find_unique(where={"slackId": user_id})
    if not user or not user.admin:
        await send_heartbeat(
            f"Attempted to edit team tag by non-admin user <@{user_id}>"
        )
        return

    await env.db.tag.update(
        where={"id": tag_id},
        data={"name": name, "description": description},
    )

    logging.info(f"Updated team tag id={tag_id} name={name} by <@{user_id}>")

    from nephthys.events.app_home_opened import open_app_home

    await open_app_home("team-tags", client, user_id)
