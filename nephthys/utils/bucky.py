import logging

import aiohttp

from nephthys.utils.env import env


async def upload_file(
    file: bytes,
    filename: str,
    content_type: str,
) -> str | None:
    api = "https://bucky.hackclub.com"
    data = aiohttp.FormData()
    data.add_field("file", file, filename=filename, content_type=content_type)
    async with env.session.post(api, data=data) as resp:
        if resp.status != 200:
            logging.error(
                f"Failed to upload image: {resp.status} - {await resp.text()}"
            )
            return None
        url = await resp.text()
    return url
