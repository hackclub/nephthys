from nephthys.views.home.components.header import get_header
from prisma.models import User


async def get_stats_view(user: User):
    return {
        "type": "home",
        "blocks": [
            *get_header(user, "my-stats"),
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": ":rac_info: My Stats",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ":rac_cute: weh im just a silly raccoon, did you expect me to have stats :rac_ded: i don't even have a job >:(",
                },
            },
        ],
    }
