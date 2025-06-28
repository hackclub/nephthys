from slack_bolt.context.ack.async_ack import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.tasks.update_helpers import update_helpers
from nephthys.utils.env import env


async def channel_join(ack: AsyncAck, event: dict, client: AsyncWebClient):
    await ack()
    user_id = event["user"]
    channel_id = event["channel"]

    if channel_id in [env.slack_bts_channel, env.slack_ticket_channel]:
        users = await client.usergroups_users_list(usergroup=env.slack_user_group)
        if user_id not in users.get("users", []):
            await client.conversations_kick(channel=channel_id, user=user_id)
            await client.chat_postMessage(
                channel=user_id, text=env.transcript.not_allowed_channel
            )
            await update_helpers()
    else:
        return
