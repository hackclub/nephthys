from blockkit import Actions
from blockkit import Button
from blockkit import Divider
from blockkit import Header
from blockkit import Home
from blockkit import Section

from nephthys.utils.env import env
from nephthys.views.home.components.header import get_header_components
from prisma.models import User


async def get_category_tags_view(user: User | None) -> dict:
    is_admin = bool(user and user.admin)

    header = get_header_components(user, "category-tags")

    if not is_admin:
        return Home(
            [
                *header,
                Header(":rac_info: Category Tags"),
                Section(":rac_nooo: only admins can manage category tags."),
            ]
        ).build()

    category_tags = await env.db.categorytag.find_many(order={"id": "asc"})

    tag_blocks = []
    if not category_tags:
        tag_blocks.append(Section(":rac_nooo: no category tags yet — add one below!"))
    else:
        for tag in category_tags:
            text = f"*{tag.name}*"
            if tag.slug:
                text += f"\n`{tag.slug}`"
            if tag.description:
                text += f"\n_{tag.description}_"

            tag_blocks.append(
                Section(
                    text=text,
                    accessory=Button(
                        text=":pencil2: Edit",
                        action_id="edit-category-tag",
                        value=str(tag.id),
                    ),
                )
            )

    return Home(
        [
            *header,
            Header(":rac_info: Category Tags"),
            Section(":rac_thumbs: manage category tags used by the AI classifier"),
            Divider(),
            *tag_blocks,
            Actions(
                elements=[
                    Button(
                        text=":rac_cute: add category",
                        action_id="create-category-tag",
                        style=Button.PRIMARY,
                    )
                ]
            ),
        ]
    ).build()
