import logging

from nephthys.database.tables import TeamTag
from nephthys.database.tables import User
from nephthys.database.tables import UserTagSubscription
from nephthys.views.home.components.header import get_header


async def get_team_tags_view(user: User | None) -> dict:
    header = get_header(user, "team-tags")
    is_admin = bool(user and user.admin)
    is_helper = bool(user and user.helper)
    tags = await TeamTag.objects()
    blocks = []

    if not tags:
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":rac_nooo: i couldn't scrounge up any tags{', you can make a new one below though' if is_admin else ''}",
                },
            }
        )

    for tag in tags:
        logging.info(f"Tag {tag.name} with id {tag.id} found in the database")
        subscriptions = await UserTagSubscription.objects().where(
            UserTagSubscription.tag == tag.id
        )
        logging.info(f"Tag {tag.name} has {len(subscriptions)} subscriptions")
        if subscriptions:
            sub_user_ids = [sub.user for sub in subscriptions]
            sub_users = await User.objects().where(User.id.is_in(sub_user_ids))
            subs = [u.slack_id for u in sub_users]
        else:
            subs = []
        stringified_subs = [f"<@{s}>" for s in subs]
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{tag.name}* - {''.join(stringified_subs) if stringified_subs else ':rac_nooo: no subscriptions'}",
                },
                "accessory": (
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": f":rac_cute: {'subscribe' if user.id not in subs else 'unsubscribe'}",
                            "emoji": True,
                        },
                        "action_id": "tag-subscribe",
                        "value": f"{tag.id};{tag.name}",
                        "style": "primary" if user.id not in subs else "danger",
                    }
                    if user and is_helper
                    else {}
                ),
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
                    "text": ":rac_info: Manage Team Tags",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        ":rac_thumbs: here you can manage tags and your subscriptions"
                        if is_admin
                        else (
                            ":rac_thumbs: here you can manage your tag subscriptions"
                            if is_helper
                            else ":rac_thumbs: note: you're not a helper, so you can only view tags"
                        )
                    ),
                },
            },
            {"type": "section", "text": {"type": "plain_text", "text": " "}},
            *blocks,
        ],
    }

    if is_admin:
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
                        "action_id": "create-team-tag",
                        "style": "primary",
                    }
                ],
            }
        )

    return view
