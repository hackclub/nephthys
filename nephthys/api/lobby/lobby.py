import logging
from hashlib import sha256
from secrets import token_urlsafe
from typing import Any
from urllib.parse import urlparse

import jinja2
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from nephthys.database.tables import APIKey
from nephthys.database.tables import User
from nephthys.utils.env import env
from nephthys.utils.env import TEMPLATES_DIR

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
    autoescape=jinja2.select_autoescape(["html", "jinja"]),
)
templates = Jinja2Templates(env=jinja_env)


def you_must_be_logged_in(req: Request):
    return templates.TemplateResponse(
        req, "you_must_be_logged_in.jinja", status_code=401
    )


def app_context() -> dict[str, Any]:
    return {
        "app_title": env.app_title,
    }


def bad_request(message: str) -> Response:
    return Response(
        f"bad request! >:(\n\n{message}",
        status_code=400,
    )


def is_same_origin_request(req: Request) -> bool:
    """Strict same-origin check for DELETE requests coming from browsers"""
    origin = req.headers.get("origin")
    if not origin:
        return False
    return urlparse(origin).netloc == req.url.netloc


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
        return you_must_be_logged_in(req)
    user_api_keys = (
        await APIKey.objects().where(APIKey.user == user.id).order_by(APIKey.created_at)
    )
    context = {
        "user": user,
        "api_keys": user_api_keys,
        **app_context(),
    }
    return templates.TemplateResponse(req, "api_keys.jinja", context=context)


async def create_api_key(req: Request):
    user = await get_logged_in_user(req)
    if not user:
        return you_must_be_logged_in(req)
    form_data = await req.form()
    label = form_data.get("label")

    # Validate input
    MAX_LABEL_LEN = 256
    if type(label) is not str:
        logging.warning(
            f"user_id={user.id} attempted create API key; invalid form param type {type(label)}"
        )
        return bad_request("expected a string but got a file?")
    label = label.strip()
    if not label:
        logging.info(f"user_id={user.id} attempted create API key with no label")
        return bad_request("you must specify a label for your API key.")
    if len(label) >= MAX_LABEL_LEN:
        logging.info(f"user_id={user.id} attempted create API key with too long label")
        return bad_request("your API key label is too long, woah!")

    # Validate other restrictions
    MAX_USER_API_KEYS = 500
    existing_api_keys: int = await APIKey.count().where(APIKey.user == user.id)
    if existing_api_keys >= MAX_USER_API_KEYS:
        logging.warning(f"user_id={user.id} attempted create too many API keys")
        return bad_request(
            f"that's too many API keys! please contact support if you need more than {MAX_USER_API_KEYS} API keys"
        )
    duplicate_label_api_keys = await APIKey.count().where(
        (APIKey.user == user.id) & (APIKey.label == label)
    )
    if duplicate_label_api_keys:
        logging.info(f"user_id={user.id} attempted create API key with duplicate label")
        return bad_request(
            f'you already have an API key called "{label}".\nplease choose a different label.'
        )

    api_key = "sk_neph_" + token_urlsafe(32)
    censored_api_key = api_key[:12] + "..." + api_key[-4:]
    api_key_hash = sha256(api_key.encode("utf-8")).digest()
    db_api_key = APIKey(
        label=label,
        user=user,
        api_key_hash=api_key_hash,
        api_key_censored=censored_api_key,
    )
    logging.info(
        f'user_id={user.id} created new API key label="{label}" key={censored_api_key}'
    )
    await db_api_key.save()

    context = {
        "api_key": api_key,
        **app_context(),
    }
    return templates.TemplateResponse(
        req, "api_key_created.jinja", context=context, status_code=201
    )


async def delete_api_key(req: Request):
    user = await get_logged_in_user(req)
    if not user:
        return you_must_be_logged_in(req)

    if not is_same_origin_request(req):
        logging.warning(
            f"user_id={user.id} attempted delete API key; request was not same-origin"
        )
        return bad_request("CSRF detected :O (request must be same-origin)")

    id_param = req.path_params.get("id")
    if not id_param:
        logging.info(f"user_id={user.id} attempted delete API key with no id param")
        return bad_request("no API key id specified.")
    try:
        api_key_id = int(id_param)
    except ValueError:
        logging.info(f"user_id={user.id} attempted delete API key with invalid id")
        return bad_request("invalid API key id.")

    # Important: Only allow deleting your own API keys!
    deleted = (
        await APIKey.delete()
        .where((APIKey.id == api_key_id) & (APIKey.user == user.id))
        .returning(APIKey.id)
    )
    if not deleted:
        logging.info(
            f"user_id={user.id} attempted delete non-existent/unowned API key api_key_id={api_key_id}"
        )
        return Response("no API key with that id.", status_code=404)

    logging.info(f"user_id={user.id} deleted API key id={api_key_id}")
    return Response(status_code=204)
