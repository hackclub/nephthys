import logging
import re

from asyncpg.exceptions import UniqueViolationError
from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.database.tables import CategoryTag
from nephthys.database.tables import User
from nephthys.events.app_home_opened import open_app_home
from nephthys.utils.logging import send_heartbeat
from nephthys.views.home import AppHomeView
from nephthys.views.modals.create_category_tag import get_create_category_tag_modal


async def create_category_tag_btn_callback(
    ack: AsyncAck, body: dict, client: AsyncWebClient
):
    await ack()
    user_id = body["user"]["id"]
    trigger_id = body["trigger_id"]

    user = await User.objects().where(User.slack_id == user_id).first()
    if not user or not user.admin:
        await send_heartbeat(
            f"Attempted to open create category tag modal by non-admin user <@{user_id}>"
        )
        return

    view = get_create_category_tag_modal()
    await client.views_open(trigger_id=trigger_id, view=view, user_id=user_id)


async def create_category_tag_view_callback(
    ack: AsyncAck, body: dict, client: AsyncWebClient
):
    user_id = body["user"]["id"]

    raw_name = body["view"]["state"]["values"]["category_tag_name"][
        "category_tag_name"
    ]["value"]
    name = raw_name.strip() if raw_name else ""

    raw_slug = body["view"]["state"]["values"]["category_tag_slug"][
        "category_tag_slug"
    ]["value"]
    slug = raw_slug.strip() if raw_slug else ""

    raw_description = body["view"]["state"]["values"]["category_tag_description"][
        "category_tag_description"
    ]["value"]
    description = raw_description.strip() if raw_description else ""

    if not name:
        await ack(
            response_action="errors",
            errors={"category_tag_name": "Category name cannot be empty."},
        )
        return

    if not re.fullmatch(r"[a-z0-9]+(?:_[a-z0-9]+)*", slug):
        await ack(
            response_action="errors",
            errors={
                "category_tag_slug": "Slug must be snake_case, e.g. hackatime_problems."
            },
        )
        return

    user = await User.objects().where(User.slack_id == user_id).first()
    if not user or not user.admin:
        await ack()
        await send_heartbeat(
            f"Attempted to create category tag by non-admin user <@{user_id}>"
        )
        return

    try:
        tag = CategoryTag(
            name=name,
            slug=slug,
            description=description or None,
            created_by=user.id,
        )
        await tag.save()
    except UniqueViolationError as e:
        constraint_name = getattr(e, "constraint_name", None)
        if constraint_name and "slug" in constraint_name:
            logging.warning(f"Duplicate category tag slug: {slug}")
            await ack(
                response_action="errors",
                errors={"category_tag_slug": f"The slug '{slug}' is already in use."},
            )
        else:
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
