def error_screen(header: list[dict], title: str, message: str) -> dict:
    """A basic error screen that can be rendered as a view if permissions are missing, or something like that"""
    return {
        "type": "home",
        "blocks": [
            *header,
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": title,
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "plain_text",
                    "text": message,
                    "emoji": True,
                },
            },
        ],
    }
