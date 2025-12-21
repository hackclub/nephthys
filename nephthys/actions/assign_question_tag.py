import logging
from typing import Any
from typing import Dict

from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.events.message.send_backend_message import backend_message_blocks
from nephthys.events.message.send_backend_message import backend_message_fallback_text
from nephthys.utils.env import env


async def assign_question_tag_callback(
    ack: AsyncAck, body: Dict[str, Any], client: AsyncWebClient
):
    await ack()
    user_id = body["user"]["id"]
    selected = body["actions"][0]["selected_option"]
    selected_value = selected["value"] if selected else None
    if selected_value and selected_value.lower() == "none":
        return
    try:
        tag_id = int(selected_value) if selected_value else None
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
        data={
            "questionTag": (
                {"connect": {"id": tag_id}}
                if tag_id is not None
                else {"disconnect": True}
            )
        },
        include={"openedBy": True},
    )
    if not ticket:
        logging.error(
            f"Failed to find corresponding ticket to update question tag ticket_ts={ts}"
        )
        return

    other_tickets = await env.db.ticket.count(
        where={
            "openedById": ticket.openedById,
            "id": {"not": ticket.id},
        }
    )
    if not ticket.openedBy:
        logging.error(f"Cannot find who opened ticket ticket_id={ticket.id}")
        return
    # Update the backend message so it has the new tag selected
    await client.chat_update(
        channel=channel_id,
        ts=ts,
        text=backend_message_fallback_text(
            ticket.openedBy.slackId,
            ticket.description,
            None,  # FIXME
        ),
        blocks=await backend_message_blocks(
            author_user_id=ticket.openedBy.slackId,
            msg_ts=ticket.msgTs,
            past_tickets=other_tickets,
            current_question_tag_id=tag_id,
            reopened_by=None,  # FIXME
        ),
    )

    logging.info(
        f"Updated question tag on ticket ticket_id={ticket.id} tag_id={tag_id}"
    )
