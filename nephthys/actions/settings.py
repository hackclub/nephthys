import logging

from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.utils.env import env
from nephthys.utils.logging import send_heartbeat
from nephthys.views.modals.configure_stale_days import get_configure_stale_days_modal


async def configure_stale_days_btn_callback(
    ack: AsyncAck, body: dict, client: AsyncWebClient
):
    """Opens the configure stale days modal when the configure button is clicked."""
    await ack()
    user_id = body["user"]["id"]
    trigger_id = body["trigger_id"]

    user = await env.db.user.find_unique(where={"slackId": user_id})
    if not user or not user.admin:
        await send_heartbeat(
            f"Attempted to open configure stale days modal by non-admin user <@{user_id}>"
        )
        return

    # Fetch current value
    stale_days_setting = await env.db.settings.find_unique(
        where={"key": "stale_ticket_days"}
    )
    current_value = stale_days_setting.value if stale_days_setting else None

    view = get_configure_stale_days_modal(current_value)
    await client.views_open(trigger_id=trigger_id, view=view, user_id=user_id)


async def configure_stale_days_view_callback(
    ack: AsyncAck, body: dict, client: AsyncWebClient
):
    """Handles the submission of the configure stale days modal."""
    user_id = body["user"]["id"]

    raw_days = body["view"]["state"]["values"]["stale_days"]["stale_days"]["value"]
    days = raw_days.strip() if raw_days else None

    errors = {}

    # Validate that it's a positive integer if provided
    if days:
        try:
            days_int = int(days)
            if days_int <= 0:
                errors["stale_days"] = "Must be a positive number."
        except ValueError:
            errors["stale_days"] = "Must be a valid number."

    if errors:
        await ack(response_action="errors", errors=errors)
        return

    user = await env.db.user.find_unique(where={"slackId": user_id})
    if not user or not user.admin:
        await ack()
        await send_heartbeat(
            f"Attempted to configure stale days by non-admin user <@{user_id}>"
        )
        return

    if days:
        await env.db.settings.upsert(
            where={"key": "stale_ticket_days"},
            data={
                "create": {"key": "stale_ticket_days", "value": days},
                "update": {"value": days},
            },
        )
        logging.info(f"Stale ticket days updated to {days} by <@{user_id}>")
        await send_heartbeat(
            f"Stale ticket days updated to {days} days by <@{user_id}>"
        )
    else:
        await env.db.settings.delete_many(where={"key": "stale_ticket_days"})
        logging.info(f"Stale ticket auto-close disabled by <@{user_id}>")
        await send_heartbeat(f"Stale ticket auto-close disabled by <@{user_id}>")

    await ack()

    from nephthys.events.app_home_opened import open_app_home

    await open_app_home("settings", client, user_id)


async def toggle_stale_feature_callback(
    ack: AsyncAck, body: dict, client: AsyncWebClient
):
    """Handles toggling the stale feature on/off.

    Disable: deletes the setting.
    Enable: opens the configure modal so the user must pick a value.
    """
    user_id = body["user"]["id"]
    action = body["actions"][0]["value"]

    user = await env.db.user.find_unique(where={"slackId": user_id})
    if not user or not user.admin:
        await ack()
        await send_heartbeat(
            f"Attempted to toggle stale feature by non-admin user <@{user_id}>"
        )
        return

    if action == "disable":
        await ack()
        await env.db.settings.delete_many(where={"key": "stale_ticket_days"})
        logging.info(f"Stale ticket auto-close disabled by <@{user_id}>")
        await send_heartbeat(f"Stale ticket auto-close disabled by <@{user_id}>")

        from nephthys.events.app_home_opened import open_app_home

        await open_app_home("settings", client, user_id)
    else:
        # Open the configure modal to set time
        await ack()
        trigger_id = body["trigger_id"]
        view = get_configure_stale_days_modal()
        await client.views_open(trigger_id=trigger_id, view=view, user_id=user_id)
