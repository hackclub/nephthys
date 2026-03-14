import logging
import re

from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.utils.env import env
from nephthys.utils.logging import send_heartbeat
from nephthys.views.modals.edit_category_tag import get_edit_category_tag_modal
from prisma.errors import UniqueViolationError


async def edit_category_tag_btn_callback(
    ack: AsyncAck, body: dict, client: AsyncWebClient
):
    await ack()
    user_id = body["user"]["id"]
    trigger_id = body["trigger_id"]
    tag_id = int(body["actions"][0]["value"])

    user = await env.db.user.find_unique(where={"slackId": user_id})
    if not user or not user.admin:
        await send_heartbeat(
            f"Attempted to open edit category tag modal by non-admin user <@{user_id}>"
        )
        return

    tag = await env.db.categorytag.find_unique(where={"id": tag_id})
    if not tag:
        logging.error(f"Category tag not found: id={tag_id}")
        return

    view = get_edit_category_tag_modal(tag.id, tag.name, tag.slug, tag.description)
    await client.views_open(trigger_id=trigger_id, view=view, user_id=user_id)


async def edit_category_tag_view_callback(
    ack: AsyncAck, body: dict, client: AsyncWebClient
):
    user_id = body["user"]["id"]
    callback_id = body["view"]["callback_id"]
    tag_id = int(callback_id.replace("edit_category_tag_", ""))
    values = body["view"]["state"]["values"]

    raw_name = values["category_tag_name"]["category_tag_name"]["value"]
    name = raw_name.strip() if raw_name else ""

    raw_slug = values["category_tag_slug"]["category_tag_slug"]["value"]
    slug = raw_slug.strip() if raw_slug else None

    raw_description = values["category_tag_description"]["category_tag_description"]["value"]
    description = raw_description.strip() if raw_description else None

    errors = {}

    if not name:
        errors["category_tag_name"] = "Category name cannot be empty."

    if slug and not re.match(r"^[a-z0-9_]+$", slug):
        errors["category_tag_slug"] = (
            "Slug must be snake_case (lowercase letters, numbers, and underscores only)."
        )

    if errors:
        await ack(response_action="errors", errors=errors)
        return

    user = await env.db.user.find_unique(where={"slackId": user_id})
    if not user or not user.admin:
        await ack()
        await send_heartbeat(
            f"Attempted to edit category tag by non-admin user <@{user_id}>"
        )
        return

    try:
        await env.db.categorytag.update(
            where={"id": tag_id},
            data={"name": name, "slug": slug, "description": description},
        )
    except UniqueViolationError as e:
        logging.warning(f"Duplicate category tag: {e}")
        error_field = "category_tag_slug" if slug and "slug" in str(e) else "category_tag_name"
        error_msg = f"A category tag with this {'slug' if error_field == 'category_tag_slug' else 'name'} already exists."
        await ack(response_action="errors", errors={error_field: error_msg})
        return

    await ack()

    from nephthys.events.app_home_opened import open_app_home

    await open_app_home("category-tags", client, user_id)
