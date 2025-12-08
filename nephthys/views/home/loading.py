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
                "image_url": "https://hc-cdn.hel1.your-objectstorage.com/s/v3/1c1fc5fb03b8bf46c6ab047c97f962ed930616f0_loading-hugs.gif",
                "alt_text": "Loading...",
            },
        ],
    }
