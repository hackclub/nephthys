import logging
from typing import Any
from typing import Dict

from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.database.tables import TagsOnTickets
from nephthys.database.tables import Ticket
from nephthys.database.tables import User
from nephthys.database.tables import UserTagSubscription
from nephthys.utils.logging import send_heartbeat
from nephthys.utils.ticket_methods import get_backend_message_link
from nephthys.utils.ticket_methods import get_question_message_link


async def assign_team_tag_callback(
    ack: AsyncAck, body: Dict[str, Any], client: AsyncWebClient
):
    await ack()
    user_id = body["user"]["id"]
    raw_tags = body["actions"][0]["selected_options"]
    tags = [
        {"name": tag["text"]["text"], "value": int(tag["value"])}
        for tag in raw_tags
        if "value" in tag
    ]
    logging.info(tags)
    channel_id = body["channel"]["id"]
    ts = body["message"]["ts"]

    user = await User.objects().where(User.slack_id == user_id).first()
    if not user or not user.helper:
        await client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            text="You are not authorized to assign tags.",
        )
        return

    ticket = await Ticket.objects().where(Ticket.ticket_ts == ts).first()
    if not ticket:
        await send_heartbeat(
            f"Failed to find ticket with ts {ts} in channel {channel_id}."
        )
        return

    existing_tags = await TagsOnTickets.objects().where(
        TagsOnTickets.ticket == ticket.id
    )

    existing_tag_ids = [t.tag for t in existing_tags]
    new_tags = [tag for tag in tags if tag["value"] not in existing_tag_ids]
    old_tags = [t for t in existing_tags if t.tag not in [tag["value"] for tag in tags]]

    logging.info(f"New: {new_tags}, Old: {old_tags}")

    for tag in new_tags:
        link = TagsOnTickets(tag=tag["value"], ticket=ticket.id)
        await link.save()

    for old_tag in old_tags:
        await old_tag.remove()

    subs = await UserTagSubscription.objects().where(
        UserTagSubscription.tag.is_in([tag["value"] for tag in new_tags])
    )

    sub_user_ids = [s.user for s in subs]
    if user.id in sub_user_ids:
        sub_user_ids.remove(user.id)

    db_users = await User.objects().where(User.id.is_in(sub_user_ids))

    users = []
    for db_user in db_users:
        tag_ids = [s.tag for s in subs if s.user == db_user.id]
        users.append(
            {
                "id": db_user.slack_id,
                "tags": tag_ids,
            }
        )

    url = get_question_message_link(ticket)
    ticket_url = get_backend_message_link(ticket)

    for u in users:
        formatted_tags = ", ".join(
            [tag["name"] for tag in new_tags if tag["value"] in u["tags"]]
        )
        await client.chat_postMessage(
            channel=u["id"],
            text=(
                f"New ticket for {formatted_tags}! *{ticket.title}*\n"
                f"<{url}|ticket> <{ticket_url}|bts ticket>"
            ),
        )
