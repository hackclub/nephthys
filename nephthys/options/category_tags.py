import logging

from thefuzz import fuzz
from thefuzz import process

from nephthys.utils.env import env


async def get_category_tags(payload: dict) -> list[dict[str, dict[str, str] | str]]:
    tags = await env.db.categorytag.find_many()
    if not tags:
        return []

    keyword = payload.get("value")
    if keyword:
        tag_names = [tag.name for tag in tags]
        scores = process.extract(keyword, tag_names, scorer=fuzz.ratio, limit=100)
        matching_tags = [tags[tag_names.index(score[0])] for score in scores]
    else:
        matching_tags = tags

    res = [
        {
            "text": {"type": "plain_text", "text": f"{tag.name}"},
            "value": str(tag.id),
        }
        for tag in matching_tags
    ]
    logging.debug(res)
    return res
