from blockkit import Context
from blockkit import Input
from blockkit import Modal
from blockkit import PlainTextInput
from blockkit import Text


def get_edit_category_tag_modal(
    tag_id: int,
    name: str,
    slug: str | None,
    description: str | None,
):
    blocks: list = [
        Input(
            label="Category name",
            block_id="category_tag_name",
            element=PlainTextInput(
                action_id="category_tag_name",
                initial_value=name,
            ),
        ),
    ]

    # Slug: show read-only if present, editable input if not
    if slug:
        blocks.append(Context(elements=[Text(text=f"*Slug:* `{slug}`", type="mrkdwn")]))
    else:
        blocks.append(
            Input(
                label="Slug (snake_case ID)",
                block_id="category_tag_slug",
                optional=True,
                element=PlainTextInput(
                    action_id="category_tag_slug",
                    placeholder="e.g. payouts_issue or fulfillment_query",
                ),
            )
        )

    blocks.append(
        Input(
            label="Description (helps AI pick this category)",
            block_id="category_tag_description",
            optional=True,
            element=PlainTextInput(
                action_id="category_tag_description",
                multiline=True,
                placeholder="What kinds of questions should be tagged with this?",
                initial_value=description if description else None,
            ),
        )
    )

    return Modal(
        title=":pencil2: edit category",
        callback_id=f"edit_category_tag_{tag_id}",
        submit=":rac_thumbs: save",
        blocks=blocks,
    ).build()
