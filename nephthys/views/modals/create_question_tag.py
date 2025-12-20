def get_create_question_tag_modal():
    return {
        "type": "modal",
        "callback_id": "create_question_tag",
        "title": {
            "type": "plain_text",
            "text": "Create question tag",
            "emoji": True,
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": """
Question tags are used to keep track of how often specific questions are being asked, so tag names should be brief but specific enough to uniquely identify the question.

Examples:
• Missing CSS on site
• What is Flavortown?
• "You're not eligible" when trying to ship project
                    """,
                },
            },
            {
                "type": "input",
                "block_id": "tag_label",
                "label": {
                    "type": "plain_text",
                    "text": "Question label",
                },
                "element": {
                    "type": "plain_text_input",
                    "action_id": "tag_label",
                },
            },
        ],
        "submit": {
            "type": "plain_text",
            "text": ":rac_question: Create!",
            "emoji": True,
        },
    }
