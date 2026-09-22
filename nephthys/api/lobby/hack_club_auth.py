import logging

from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.responses import Response

from nephthys.database.tables import User
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


async def log_in(req: Request):
    if not hca_config:
        return hca_not_configured_response

    hca = oauth.create_client("hca")
    redirect_uri = env.base_url + "/oauth/callback"
    return await hca.authorize_redirect(req, redirect_uri)


async def authorize(req: Request):
    if not hca_config:
        return hca_not_configured_response

    token = await oauth.hca.authorize_access_token(req)
    res = await oauth.hca.get("me", token=token)
    res.raise_for_status()
    identity: dict = res.json()["identity"]
    hca_id = identity["id"]
    slack_id = identity.get("slack_id")
    if not slack_id:
        logging.info(f"Failed log-in attempt (no Slack ID) hca_id={hca_id}")
        return Response(
            "Sorry! You must have a Hack Club Slack account to access the Nephthys Lobby.",
            status_code=403,
        )

    # Upsert the user in the database
    db_user = await User.objects().get_or_create(User.slack_id == slack_id)

    # Store details in a signed session cookie - the user is now "logged in"
    req.session["hca_id"] = hca_id
    req.session["slack_id"] = slack_id
    req.session["user_id"] = db_user.id

    logging.info(
        f"User signed in hca_id={hca_id} slack_id={slack_id} user_id={db_user.id}"
    )
    return RedirectResponse(url="/lobby")


async def log_out(req: Request):
    req.session.clear()
    return RedirectResponse(url="/lobby")
