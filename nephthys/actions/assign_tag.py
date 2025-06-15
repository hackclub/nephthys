import logging
from typing import Any
from typing import Dict

from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.utils.env import env
from nephthys.utils.logging import send_heartbeat


async def assign_tag_callback(
    ack: AsyncAck, body: Dict[str, Any], client: AsyncWebClient
):
    await ack()
    user_id = body["user"]["id"]
    raw_tags = body["actions"][0]["selected_options"]
    tags = [
        {"name": tag["text"]["text"], "value": tag["value"]}
        for tag in raw_tags
        if "value" in tag
    ]
    logging.info(tags)
    channel_id = body["channel"]["id"]
    ts = body["message"]["ts"]

    user = await env.db.user.find_unique(where={"slackId": user_id})
    if not user or not user.helper:
        await client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            text="You are not authorized to assign tags.",
        )
        return

    ticket = await env.db.ticket.find_unique(
        where={"ticketTs": ts}, include={"tagsOnTickets": True}
    )
    if not ticket:
        await send_heartbeat(
            f"Failed to find ticket with ts {ts} in channel {channel_id}."
        )
        return
    if ticket.tagsOnTickets:
        new_tags = [
            tag
            for tag in tags
            if tag["value"] not in [t.tagId for t in ticket.tagsOnTickets]
        ]
        old_tags = [
            tag
            for tag in ticket.tagsOnTickets
            if tag.tagId not in [t["value"] for t in tags]
        ]
    else:
        new_tags = tags
        old_tags = []
    logging.info(f"New: {new_tags}, Old: {old_tags}")

    await env.db.tagsontickets.create_many(
        data=[{"tagId": tag["value"], "ticketId": ticket.id} for tag in new_tags]
    )

    await env.db.tagsontickets.delete_many(
        where={"tagId": {"in": [tag.tagId for tag in old_tags]}, "ticketId": ts}
    )

    tags = await env.db.usertagsubscription.find_many(
        where={"tagId": {"in": [tag["value"] for tag in new_tags]}}
    )

    users = [
        {
            "id": tag.userId,
            "tags": [tag.tagId for tag in tags if tag.userId == tag.userId],
        }
        for tag in tags
    ]
    url = f"https://hackclub.slack.com/archives/{env.slack_help_channel}/p{ticket.msgTs.replace('.', '')}"

    for user in users:
        formatted_tags = ", ".join(
            [tag["name"] for tag in new_tags if tag["value"] in user["tags"]]
        )
        await client.chat_postMessage(
            channel=user["id"], text=f"New ticket for {formatted_tags}!\n{url}"
        )
