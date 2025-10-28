from nephthys.utils.env import env


def get_header():
    return {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": f":rac_cute: {env.app_title}",
            "emoji": True,
        },
    }
