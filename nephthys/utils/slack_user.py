import logging

from slack_sdk.web.async_slack_response import AsyncSlackResponse

from nephthys.utils.env import env


class UserProfileWrapper:
    def __init__(self, users_info_response: AsyncSlackResponse):
        user_data = users_info_response.get("user")
        if not user_data:
            raise ValueError(f"Slack user not found: {users_info_response}")
        self.raw_data = user_data

    def display_name(self) -> str:
        display_name = (
            self.raw_data["profile"].get("display_name")
            or self.raw_data["profile"].get("real_name")
            or self.raw_data["name"]
        )
        # This should never actually be empty but if it is, that is a major issue
        if not display_name:
            logging.error(
                f"SOMETHING HAS GONE TERRIBLY WRONG - user has no username: {self.raw_data}"
            )
            return ""  # idk
        return display_name

    def profile_pic_512x(self) -> str | None:
        return self.raw_data["profile"].get("image_512")


async def get_user_profile(slack_id: str) -> UserProfileWrapper:
    """Retrieve the user's display name from Slack given their Slack ID."""
    response = await env.slack_client.users_info(user=slack_id)
    return UserProfileWrapper(response)
