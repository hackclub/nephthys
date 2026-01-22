from nephthys.utils.env import env
from nephthys.views.home.components.header import get_header


def get_loading_view(home_type: str):
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
                "image_url": f"{env.base_url}/public/loading.gif",
                "alt_text": "Loading...",
            },
        ],
    }
