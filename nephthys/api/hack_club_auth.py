import logging

from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from starlette.responses import Response

from nephthys.utils.env import env

hca_config = env.hca

if hca_config:
    oauth = OAuth()
    oauth.register(
        name="hca",
        client_id=hca_config.client_id,
        client_secret=hca_config.client_secret,
        authorize_url=f"{hca_config.base_url}/oauth/authorize",
        authorize_params=None,
        access_token_url=f"{hca_config.base_url}/oauth/token",
        access_token_params=None,
        api_base_url=f"{hca_config.base_url}/api/v1/",
        client_kwargs={"scope": "slack_id"},
    )

hca_not_configured_response = Response(
    "Hack Club Auth integration is not configured on this Nephthys instance",
    status_code=500,
)


async def login(req: Request):
    if not hca_config:
        return hca_not_configured_response

    hca = oauth.create_client("hca")
    redirect_uri = req.url_for("authorize")
    return await hca.authorize_redirect(req, redirect_uri)


async def authorize(req: Request):
    if not hca_config:
        return hca_not_configured_response

    token = await oauth.hca.authorize_access_token(req)
    res = await oauth.hca.get("me", token=token)
    res.raise_for_status()
    identity = res.json()["identity"]
    hca_id = identity["id"]
    slack_id = identity["slack_id"]
    logging.info(f"User signed in hca_id={hca_id} slack_id={slack_id}")
    return Response("yay!")
