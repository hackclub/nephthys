import logging
from typing import Any
from typing import Dict

from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.utils.env import env


async def assign_question_tag_callback(
    ack: AsyncAck, body: Dict[str, Any], client: AsyncWebClient
):
    await ack()
    user_id = body["user"]["id"]
    selected = body["actions"][0]["selected_option"]
    if not selected:
        return
    selected_value = selected["value"]
    if selected_value.lower() == "none":
        return
    try:
        tag_id = int(selected_value)
    except ValueError as e:
        raise ValueError(f"Invalid tag ID: {selected_value}") from e

    channel_id = body["channel"]["id"]
    ts = body["message"]["ts"]

    user = await env.db.user.find_unique(where={"slackId": user_id})
    if not user or not user.helper:
        logging.warning(
            f"Unauthorized user attempted to assign question tag user_id={user_id}"
        )
        await client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            text="You are not authorized to assign tags.",
        )
        return

    ticket = await env.db.ticket.update(
        where={"ticketTs": ts},
        data={"questionTag": {"connect": {"id": tag_id}}},
    )
    if not ticket:
        logging.error(
            f"Failed to find corresponding ticket to update question tag ticket_ts={ts}"
        )
        return
    logging.info(
        f"Assigned question tag to ticket ticket_id={ticket.id} tag_id={tag_id}"
    )
