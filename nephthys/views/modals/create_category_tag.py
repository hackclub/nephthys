from blockkit import Input
from blockkit import Modal
from blockkit import PlainTextInput


def get_create_category_tag_modal():
    return Modal(
        title=":rac_info: new category",
        callback_id="create_category_tag",
        submit=":rac_question: create",
        blocks=[
            Input(
                label="Category name",
                block_id="category_tag_name",
                element=PlainTextInput(action_id="category_tag_name"),
            ),
            Input(
                label="Slug (snake_case ID)",
                block_id="category_tag_slug",
                element=PlainTextInput(
                    action_id="category_tag_slug",
                    placeholder="e.g. payouts_issue or fulfillment_query",
                ),
            ),
            Input(
                label="Description (helps AI pick this category)",
                block_id="category_tag_description",
                optional=True,
                element=PlainTextInput(
                    action_id="category_tag_description",
                    multiline=True,
                    placeholder="What kinds of questions should be tagged with this?",
                ),
            ),
        ],
    ).build()
