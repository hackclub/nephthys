from typing import Any
from typing import Dict

from slack_bolt.context.ack.async_ack import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.utils.env import env


async def open_manage_tags_modal(
    ack: AsyncAck, body: Dict[str, Any], client: AsyncWebClient
):
    await ack()
    category_tags = await env.db.categorytag.find_many(order={"name": "asc"})
    current_tags = "\n".join([tag.name for tag in category_tags])

    await client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "save-tags",
            "title": {"type": "plain_text", "text": "Manage Category Tags"},
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
                        "text": "Category Tags (one per line)",
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

    existing_tags = await env.db.categorytag.find_many()
    existing_map = {tag.name: tag for tag in existing_tags}

    to_delete_ids = [
        tag.id for name, tag in existing_map.items() if name not in new_tags
    ]
    to_create_names = [name for name in new_tags if name not in existing_map]

    if to_delete_ids:
        await env.db.categorytag.delete_many(where={"id": {"in": to_delete_ids}})

    if to_create_names:
        user_id = body["user"]["id"]

        db_user = await env.db.user.find_unique(where={"slackId": user_id})

        for name in to_create_names:
            data = {"name": name}
            if db_user:
                data["createdBy"] = {"connect": {"id": db_user.id}}
            await env.db.categorytag.create(data=data)

    await client.chat_postMessage(
        channel=body["user"]["id"],
        text=f"Would you look at that! Category tags updated!\n {len(new_tags)} tags saved :yay:",
    )
