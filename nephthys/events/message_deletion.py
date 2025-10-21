import logging
from typing import Any
from typing import Dict

import slack_sdk.errors
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.utils.env import env
from nephthys.utils.logging import send_heartbeat


async def handle_question_deletion(
    client: AsyncWebClient, channel: str, deleted_msg: Dict[str, Any]
) -> None:
    """Handle deletion of a top-level question message in the help channel.

    - If the thread has non-bot messages, do nothing.
    - Otherwise, deletes the bot messages in the thread and removes the ticket from the DB.
      - This behaviour is similar to `?thread`, except it removes the ticket from the DB instead of marking it as resolved.
    """
    try:
        thread_history = await client.conversations_replies(
            channel=channel, ts=deleted_msg["ts"]
        )
    except slack_sdk.errors.SlackApiError as e:
        if e.response.get("error") == "thread_not_found":
            # Nothing to clean up; we good
            return
        else:
            raise e
    bot_info = await env.slack_client.auth_test()
    bot_user_id = bot_info.get("user_id")
    messages_to_delete = []
    for msg in thread_history["messages"]:
        if msg["user"] == bot_user_id:
            messages_to_delete.append(msg)
        elif msg["ts"] != deleted_msg["ts"]:
            # Don't clear the thread if there are non-bot messages in there
            return

    # Delete ticket from DB
    await env.db.ticket.delete(where={"msgTs": deleted_msg["ts"]})

    # Delete messages
    await send_heartbeat(
        f"Removing my {len(messages_to_delete)} message(s) in a thread because the question was deleted."
    )
    for msg in messages_to_delete:
        await client.chat_delete(
            channel=channel,
            ts=msg["ts"],
        )


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
    if event.get("subtype") == "message_deleted":
        # This means the message has been completely deleted with out leaving a "tombstone"
        # No thread means no messages to delete, but we should delete any associated ticket from the DB
        await env.db.ticket.delete(where={"msgTs": deleted_msg["ts"]})
    else:
        # A parent message (i.e. top-level message in help channel) has been deleted
        await handle_question_deletion(client, event["channel"], deleted_msg)
