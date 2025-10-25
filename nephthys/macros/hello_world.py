from nephthys.macros.types import Macro
from nephthys.utils.env import env
from nephthys.utils.ticket_methods import reply_to_ticket


class HelloWorld(Macro):
    name = "hii"

    async def run(self, ticket, helper, **kwargs):
        """
        A simple hello world macro that does nothing.
        """
        user_info = await env.slack_client.users_info(user=helper.slackId)
        name = (
            user_info["user"]["profile"].get("display_name")
            or user_info["user"]["profile"].get("real_name")
            or user_info["user"]["name"]
        )
        await reply_to_ticket(
            text=f"hey, {name}! i'm heidi :rac_shy: say hi to orpheus for me would you? :rac_cute:",
            ticket=ticket,
            client=env.slack_client,
        )
