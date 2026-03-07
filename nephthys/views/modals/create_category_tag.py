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
            # future: description
            # future: slug
        ],
    ).build()
