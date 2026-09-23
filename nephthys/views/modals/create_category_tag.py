from blockkit import Input
from blockkit import Modal
from blockkit import PlainTextInput


def get_create_category_tag_modal():
    return Modal(
        title="create new category tag!",
        callback_id="create_category_tag",
        submit=":rac_question: create",
        blocks=[
            Input(
                label="Category name",
                block_id="category_tag_name",
                element=PlainTextInput(
                    action_id="category_tag_name", placeholder="Hackatime problems"
                ),
                hint="Names can be edited later.",
            ),
            Input(
                label="Slug",
                block_id="category_tag_slug",
                element=PlainTextInput(
                    action_id="category_tag_slug", placeholder="hackatime_problems"
                ),
                hint="Immutable snake_case slug, used for API responses and metrics.",
            ),
            Input(
                label="Description",
                block_id="category_tag_description",
                element=PlainTextInput(
                    action_id="category_tag_description",
                    multiline=True,
                    placeholder='issues with "Hackatime"; coding time not being tracked at all',
                ),
                hint="Recommended - provide a brief description and/or examples of what this category should include.",
                optional=True,
            ),
        ],
    ).build()
