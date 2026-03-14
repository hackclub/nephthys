def get_edit_team_tag_modal(tag_id: int, name: str, description: str | None):
    return {
        "type": "modal",
        "callback_id": f"edit_team_tag_{tag_id}",
        "title": {"type": "plain_text", "text": ":pencil2: edit tag", "emoji": True},
        "submit": {"type": "plain_text", "text": ":rac_thumbs: save", "emoji": True},
        "blocks": [
            {
                "type": "input",
                "block_id": "tag_name",
                "label": {"type": "plain_text", "text": "Name", "emoji": True},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "tag_name",
                    "initial_value": name,
                },
            },
            {
                "type": "input",
                "block_id": "tag_description",
                "optional": True,
                "label": {
                    "type": "plain_text",
                    "text": "Description (optional)",
                    "emoji": True,
                },
                "element": {
                    "type": "plain_text_input",
                    "action_id": "tag_description",
                    "multiline": True,
                    "placeholder": {"type": "plain_text", "text": "What is this tag for?"},
                    **({"initial_value": description} if description else {}),
                },
            },
        ],
    }
