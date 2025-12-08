import logging

from nephthys.utils.env import env
from nephthys.views.home.components.error_screen import error_screen
from nephthys.views.home.components.header import get_header
from prisma.models import User


async def get_manage_tags_view(user: User | None) -> dict:
    header = get_header(user, "tags")
    if not user or not user.helper:
        return error_screen(
            header,
            ":rac_info: you're not a helper!",
            "Only helpers can subscribe to tags.",
        )

    tags = await env.db.tag.find_many(include={"userSubscriptions": True})
    blocks = []

    if not tags:
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":rac_nooo: i couldn't scrounge up any tags{', you can make a new one below though' if user.admin else ''}",
                },
            }
        )

    for tag in tags:
        logging.info(f"Tag {tag.name} with id {tag.id} found in the database")
        logging.info(
            f"Tag {tag.name} has {len(tag.userSubscriptions) if tag.userSubscriptions else 0} subscriptions"
        )
        if tag.userSubscriptions:
            subIds = [user.userId for user in tag.userSubscriptions]

            subUsers = await env.db.user.find_many(where={"id": {"in": subIds}})

            subs = [user.slackId for user in subUsers]
        else:
            subs = []
        stringified_subs = [f"<@{user}>" for user in subs]
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{tag.name}* - {''.join(stringified_subs) if stringified_subs else ':rac_nooo: no subscriptions'}",
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": f":rac_cute: {'subscribe' if user.id not in subs else 'unsubscribe'}",
                        "emoji": True,
                    },
                    "action_id": "tag-subscribe",
                    "value": f"{tag.id};{tag.name}",
                    "style": "primary" if user.id not in subs else "danger",
                },
            }
        )

    view = {
        "type": "home",
        "blocks": [
            *header,
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": ":rac_info: Manage Tags",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ":rac_thumbs: here you can manage tags and your subscriptions"
                    if user.admin
                    else ":rac_thumbs: here you can manage your tag subscriptions",
                },
            },
            {"type": "section", "text": {"type": "plain_text", "text": " "}},
            # {"type": "divider"},
            *blocks,
        ],
    }

    if user.admin:
        view["blocks"].append(
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": ":rac_cute: add a tag?",
                            "emoji": True,
                        },
                        "action_id": "create-tag",
                        "style": "primary",
                    }
                ],
            }
        )

    return view
