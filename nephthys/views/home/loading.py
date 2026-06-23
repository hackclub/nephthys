from nephthys.events.app_home_opened import AppHomeView
from nephthys.utils.env import env
from nephthys.views.home.components.header import get_header


def get_loading_view(home_type: AppHomeView):
    return {
        "type": "home",
        "blocks": [
            *get_header(user=None, current=home_type),
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": ":hourglass_flowing_sand: loading...",
                },
            },
            {
                "type": "image",
                "image_url": r"https://raw.githubusercontent.com/hackclub/nephthys/refs/heads/main/nephthys/public/loading.gif",
                "alt_text": "Loading...",
            },
        ],
    }
