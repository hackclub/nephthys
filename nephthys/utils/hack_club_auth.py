from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request

from nephthys.utils.env import env

config = env.hca

if config is None:
    raise ValueError("hack_club_auth module was imported without HCA config being set")

oauth = OAuth()
oauth.register(
    name="hca",
    client_id=config.client_id,
    client_secret=config.client_secret,
    authorize_url=f"{config.base_url}/oauth/authorize",
    authorize_params=None,
    access_token_url=f"{config.base_url}/oauth/token",
    access_token_params=None,
    # api_base_url="https://api.github.com/",
    client_kwargs={"scope": "slack_id"},
)


def login(req: Request):
    hca = oauth.create_client("hca")
    redirect_uri = "https://example.com/authorize"
    return hca.authorize_redirect(req, redirect_uri)


def authorize(req: Request):
    token = oauth.hca.authorize_access_token(req)
    resp = oauth.hca.get("user", token=token)
    resp.raise_for_status()
    _profile = resp.json()
    # do something with the token and profile
    return "..."
