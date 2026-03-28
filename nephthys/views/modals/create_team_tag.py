def get_create_team_tag_modal():
    return {
        "type": "modal",
        "callback_id": "create_team_tag",
        "title": {
            "type": "plain_text",
            "text": ":rac_info: create a tag!",
            "emoji": True,
        },
        "submit": {
            "type": "plain_text",
            "text": ":rac_question: add tag?",
            "emoji": True,
        },
        "blocks": [
            {
                "type": "input",
                "block_id": "tag_name",
                "label": {
                    "type": "plain_text",
                    "text": "Name",
                    "emoji": True,
                },
                "element": {
                    "type": "plain_text_input",
                    "action_id": "tag_name",
                },
            },
            {
                "type": "input",
                "block_id": "tag_description",
                "optional": True,
                "label": {
                    "type": "plain_text",
                    "text": "Description",
                    "emoji": True,
                },
                "element": {
                    "type": "plain_text_input",
                    "action_id": "tag_description",
                    "multiline": True,
                    "placeholder": {
                        "type": "plain_text",
                        "text": "What is this tag for?",
                    },
                },
            },
        ],
    }
