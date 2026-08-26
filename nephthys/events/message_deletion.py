import logging
from typing import Any
from typing import Dict

from slack_sdk.web.async_client import AsyncWebClient

from nephthys.database.tables import Ticket
from nephthys.utils.ticket_methods import discard_ticket


async def handle_question_deletion(
    client: AsyncWebClient, deleted_msg: Dict[str, Any]
) -> None:
    """Discard a ticket when its top-level help question has been deleted."""
    ticket = await Ticket.objects().where(Ticket.msg_ts == deleted_msg["ts"]).first()
    if not ticket:
        logging.info(
            "Deleted question has no associated ticket, ts=%s", deleted_msg["ts"]
        )
        return
    await discard_ticket(ticket, client)


async def on_message_deletion(event: Dict[str, Any], client: AsyncWebClient) -> None:
    """Handles the two types of message deletion events
    (i.e. a message being turned into a tombstone, and a message being fully deleted)."""
    deleted_msg = event.get("previous_message")
    if not deleted_msg:
        logging.warning("No previous_message found in message deletion event")
        return
    is_in_thread = (
        "thread_ts" in deleted_msg and deleted_msg["ts"] != deleted_msg["thread_ts"]
    )
    if is_in_thread:
        return
    # A parent can either become a tombstone or disappear entirely. Both forms
    # must discard the ticket and its Slack artifacts.
    await handle_question_deletion(client, deleted_msg)
