from blockkit import Context
from blockkit import Input
from blockkit import Modal
from blockkit import PlainTextInput
from blockkit import Text

from nephthys.database.tables import CategoryTag


def get_edit_category_tag_modal(tag: CategoryTag):
    return Modal(
        title="edit category tag",
        callback_id="edit_category_tag",
        submit=":rac_question: save",
        private_metadata=str(tag.id),
        blocks=[
            Context([Text(f"Slug: `{tag.slug}` (this can't be changed)")]),
            Input(
                label="Category name",
                block_id="category_tag_name",
                element=PlainTextInput(
                    action_id="category_tag_name", initial_value=tag.name
                ),
            ),
            Input(
                label="Description",
                block_id="category_tag_description",
                element=PlainTextInput(
                    action_id="category_tag_description",
                    initial_value=tag.description,
                    multiline=True,
                ),
                hint="Recommended - provide a brief description and/or examples of what this category should include.",
                optional=True,
            ),
        ],
    ).build()
