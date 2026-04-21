import logging
from typing import Any
from typing import Dict

from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.database.tables import Ticket
from nephthys.database.tables import User
from nephthys.events.message.send_backend_message import backend_message_blocks
from nephthys.events.message.send_backend_message import backend_message_fallback_text


async def assign_category_tag_callback(
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

    user = await User.objects().where(User.slack_id == user_id).first()
    if not user or not user.helper:
        logging.warning(
            f"Unauthorized user attempted to assign category tag user_id={user_id}"
        )
        await client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            text="You are not authorized to assign tags.",
        )
        return

    await Ticket.update(
        {
            Ticket.category_tag: tag_id,
        }
    ).where(Ticket.ticket_ts == ts)

    ticket = (
        await Ticket.objects(Ticket.opened_by, Ticket.reopened_by)
        .where(Ticket.ticket_ts == ts)
        .first()
    )
    if not ticket:
        logging.error(
            f"Failed to find corresponding ticket to update category tag ticket_ts={ts}"
        )
        return

    other_tickets = await Ticket.count().where(
        (Ticket.opened_by == ticket.opened_by) & (Ticket.id != ticket.id)
    )
    if not ticket.opened_by:
        logging.error(f"Cannot find who opened ticket ticket_id={ticket.id}")
        return
    # Update the backend message so it has the new tag selected
    await client.chat_update(
        channel=channel_id,
        ts=ts,
        text=backend_message_fallback_text(
            author_user_id=ticket.opened_by.slack_id,
            description=ticket.description,
            reopened_by=ticket.reopened_by,
        ),
        blocks=await backend_message_blocks(
            author_user_id=ticket.opened_by.slack_id,
            msg_ts=ticket.msg_ts,
            past_tickets=other_tickets,
            current_category_tag_id=tag_id,
            reopened_by=ticket.reopened_by,
        ),
    )

    logging.info(
        f"Updated category tag on ticket ticket_id={ticket.id} tag_id={tag_id}"
    )
