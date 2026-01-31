from typing import Any
from typing import Dict

from slack_bolt.context.ack.async_ack import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.utils.env import env


async def get_system_settings():
    settings = await env.db.systemsettings.find_first()
    if not settings:
        settings = await env.db.systemsettings.create(data={"questionTags": []})
    return settings


async def open_manage_tags_modal(
    ack: AsyncAck, body: Dict[str, Any], client: AsyncWebClient
):
    await ack()
    settings = await get_system_settings()
    current_tags = "\n".join(settings.questionTags)

    await client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "save-tags",
            "title": {"type": "plain_text", "text": "Manage Question Tags"},
            "submit": {"type": "plain_text", "text": "Save"},
            "close": {"type": "plain_text", "text": "Cancel"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "tags_block",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "tags_input",
                        "multiline": True,
                        "initial_value": current_tags,
                        "placeholder": {
                            "type": "plain_text",
                            "text": "Enter tags, one per line",
                        },
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Question Tags (one per line)",
                    },
                }
            ],
        },
    )


async def handle_manage_tags_save(
    ack: AsyncAck, body: Dict[str, Any], client: AsyncWebClient
):
    await ack()
    tags_input = body["view"]["state"]["values"]["tags_block"]["tags_input"]["value"]

    new_tags = [tag.strip() for tag in tags_input.split("\n") if tag.strip()]

    settings = await env.db.systemsettings.find_first()

    if settings:
        await env.db.systemsettings.update(
            where={"id": settings.id}, data={"questionTags": new_tags}
        )
    else:
        await env.db.systemsettings.create(data={"questionTags": new_tags})

    await client.chat_postMessage(
        channel=body["user"]["id"],
        text=f"Would you look at that! Question tags updated!\n {len(new_tags)} tags saved :yay:",
    )
