import logging

from nephthys.database.tables import User
from nephthys.utils.env import env


async def update_helpers():
    res = await env.slack_client.conversations_members(channel=env.slack_bts_channel)
    team_ids = res.get("members", [])

    # Get bot user ID to exclude from helpers
    bot_info = await env.slack_client.auth_test()
    bot_user_id = bot_info.get("user_id")

    # Filter out bot user from team_ids
    if bot_user_id and bot_user_id in team_ids:
        team_ids = [user_id for user_id in team_ids if user_id != bot_user_id]

    if not team_ids:
        # if this happens then something concerning has happened :p
        await env.slack_client.chat_postMessage(
            channel=env.slack_bts_channel,
            text=f"No members found in the bts channel. <@{env.slack_maintainer_id}>",
        )
        return

    # unset helpers not in the team
    await User.update({User.helper: False}).where(
        (User.helper.eq(True)) & User.slack_id.not_in(team_ids)
    )

    # update existing users in the db
    await User.update({User.helper: True}).where(User.slack_id.is_in(team_ids))

    # create new users not in the db
    existing_users_in_db = await User.objects().where(User.slack_id.is_in(team_ids))
    existing_user_ids_in_db = {user.slack_id for user in existing_users_in_db}

    new_users = []
    for member_id in team_ids:
        if member_id not in existing_user_ids_in_db:
            user_info = await env.slack_client.users_info(user=member_id)
            logging.info(
                f"Creating new helper user {member_id} with info {user_info.get('name')}"
            )
            logging.info(f"User info for {member_id}: {user_info}")
            new_users.append(
                User(
                    slack_id=member_id,
                    helper=True,
                    username=user_info.get("user", {}).get("name"),
                )
            )

    if new_users:
        await User.insert(*new_users)

    # ensure the bot maintainer is an admin
    await User.update({User.admin: True}).where(
        User.slack_id == env.slack_maintainer_id
    )
    maintainer = (
        await User.objects().where(User.slack_id == env.slack_maintainer_id).first()
    )
    if not maintainer:
        logging.warning(
            f"Bot maintainer {env.slack_maintainer_id} is not a helper or in the database"
        )
    elif not maintainer.helper:
        logging.warning(f"Bot maintainer {env.slack_maintainer_id} is not a helper")
