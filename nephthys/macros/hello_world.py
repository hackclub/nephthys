from nephthys.macros.types import Macro
from nephthys.utils.env import env
from nephthys.utils.slack_user import get_user_profile
from nephthys.utils.ticket_methods import reply_to_ticket


class HelloWorld(Macro):
    name = "hii"

    async def run(self, ticket, helper, **kwargs):
        """
        A simple hello world macro that does nothing.
        """
        user = await get_user_profile(helper.slack_id)
        name = user.display_name()
        await reply_to_ticket(
            text=f"hey, {name}! i'm heidi :rac_shy: say hi to orpheus for me would you? :rac_cute:",
            ticket=ticket,
            client=env.slack_client,
        )
