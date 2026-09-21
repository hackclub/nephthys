import logging
from typing import Any

import jinja2
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from nephthys.database.tables import User
from nephthys.utils.env import env
from nephthys.utils.env import TEMPLATES_DIR

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
    autoescape=jinja2.select_autoescape(["html", "jinja"]),
)
templates = Jinja2Templates(env=jinja_env)


def app_context() -> dict[str, Any]:
    return {
        "app_title": env.app_title,
    }


async def get_logged_in_user(req: Request) -> User | None:
    session_user_id = req.session.get("user_id")
    if not session_user_id:
        return None
    user = await User.objects().get(User.id == session_user_id)
    if not user:
        logging.warning(
            f"User accessed site with invalid session user_id={session_user_id}"
        )
        req.session.clear()
    return user


async def lobby(req: Request):
    context = {
        "user": await get_logged_in_user(req),
        **app_context(),
    }
    return templates.TemplateResponse(req, "lobby.jinja", context=context)


async def api_keys(req: Request):
    user = await get_logged_in_user(req)
    if not user:
        return templates.TemplateResponse(req, "you_must_be_logged_in.jinja")
    context = {
        "user": user,
        **app_context(),
    }
    return templates.TemplateResponse(req, "api_keys.jinja", context=context)
