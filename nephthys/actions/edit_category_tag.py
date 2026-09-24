import logging

from asyncpg.exceptions import UniqueViolationError
from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.database.tables import CategoryTag
from nephthys.database.tables import User
from nephthys.events.app_home_opened import open_app_home
from nephthys.utils.logging import send_heartbeat
from nephthys.views.home import AppHomeView
from nephthys.views.modals.edit_category_tag import get_edit_category_tag_modal


async def edit_category_tag_btn_callback(
    ack: AsyncAck, body: dict, client: AsyncWebClient
):
    await ack()
    user_id = body["user"]["id"]
    trigger_id = body["trigger_id"]

    user = await User.objects().where(User.slack_id == user_id).first()
    if not user or not user.admin:
        await send_heartbeat(
            f"Attempted to open edit category tag modal by non-admin user <@{user_id}>"
        )
        return

    try:
        tag_id = int(body["actions"][0]["value"])
    except (KeyError, ValueError):
        logging.warning("Edit category tag action is missing a valid tag id")
        return

    tag = await CategoryTag.objects().where(CategoryTag.id == tag_id).first()
    if not tag:
        logging.warning(f"Attempted to edit missing category tag tag_id={tag_id}")
        return

    view = get_edit_category_tag_modal(tag)
    await client.views_open(trigger_id=trigger_id, view=view, user_id=user_id)


async def edit_category_tag_view_callback(
    ack: AsyncAck, body: dict, client: AsyncWebClient
):
    user_id = body["user"]["id"]

    values = body["view"]["state"]["values"]
    raw_name = values["category_tag_name"]["category_tag_name"]["value"]
    name = raw_name.strip() if raw_name else ""

    raw_description = values["category_tag_description"]["category_tag_description"][
        "value"
    ]
    description = raw_description.strip() if raw_description else ""

    if not name:
        await ack(
            response_action="errors",
            errors={"category_tag_name": "Category name cannot be empty."},
        )
        return

    user = await User.objects().where(User.slack_id == user_id).first()
    if not user or not user.admin:
        await ack()
        await send_heartbeat(
            f"Attempted to edit category tag by non-admin user <@{user_id}>"
        )
        return

    try:
        tag_id = int(body["view"]["private_metadata"])
    except (TypeError, ValueError):
        logging.error("Edit category tag view is missing a valid tag id")
        await ack()
        return

    try:
        await CategoryTag.update(
            {
                CategoryTag.name: name,
                CategoryTag.description: description or None,
            }
        ).where(CategoryTag.id == tag_id)
    except UniqueViolationError:
        logging.warning(f"Duplicate category tag name: {name}")
        await ack(
            response_action="errors",
            errors={
                "category_tag_name": f"A category tag named '{name}' already exists."
            },
        )
        return

    await ack()

    await open_app_home(AppHomeView.CATEGORY_TAGS, client, user_id)
