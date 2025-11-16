from nephthys.utils.env import env


async def get_user_name(slack_id: str) -> str:
    """Retrieve the user's display name from Slack given their Slack ID."""
    response = await env.slack_client.users_info(user=slack_id)
    user = response.get("user")
    if not user:
        raise ValueError(f"User with Slack ID {slack_id} not found.")
    return (
        user["profile"].get("display_name")
        or user["profile"].get("real_name")
        or user["name"]
    )
