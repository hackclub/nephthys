from typing import Any
from typing import Dict

from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.database.tables import User
from nephthys.database.tables import UserTagSubscription
from nephthys.events.app_home_opened import open_app_home
from nephthys.utils.logging import send_heartbeat


async def tag_subscribe_callback(
    ack: AsyncAck, body: Dict[str, Any], client: AsyncWebClient
):
    """
    Callback for the tag subscribe button
    """
    await ack()
    slack_id = body["user"]["id"]

    user = await User.objects().where(User.slack_id == slack_id).first()
    if not user:
        await send_heartbeat(
            f"Attempted to subscribe to tag by unknown user <@{slack_id}>"
        )
        return

    tag_id, tag_name = body["actions"][0]["value"].split(";")
    # check if user is subscribed
    existing = (
        await UserTagSubscription.objects()
        .where(
            (UserTagSubscription.tag == int(tag_id))
            & (UserTagSubscription.user == user.id)
        )
        .first()
    )
    if existing:
        await existing.remove()
    else:
        sub = UserTagSubscription(user=user.id, tag=int(tag_id))
        await sub.save()

    await open_app_home("team-tags", client, slack_id)
