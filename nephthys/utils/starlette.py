import secrets

from prometheus_client import CONTENT_TYPE_LATEST
from prometheus_client import generate_latest
from slack_bolt.adapter.starlette.async_handler import AsyncSlackRequestHandler
from starlette.applications import Starlette
from starlette.datastructures import Secret
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.responses import RedirectResponse
from starlette.responses import Response
from starlette.routing import Mount
from starlette.routing import Route
from starlette.staticfiles import StaticFiles
from starlette_exporter import PrometheusMiddleware

from nephthys.__main__ import main
from nephthys.api.lobby.hack_club_auth import authorize
from nephthys.api.lobby.hack_club_auth import log_in
from nephthys.api.lobby.hack_club_auth import log_out
from nephthys.api.lobby.lobby import api_keys
from nephthys.api.lobby.lobby import lobby
from nephthys.api.stats import stats
from nephthys.api.stats_range import stats_range
from nephthys.api.stats_v2 import stats_v2
from nephthys.api.ticket import ticket_info
from nephthys.api.tickets import tickets_list
from nephthys.api.user import user_stats
from nephthys.utils.env import env
from nephthys.utils.env import STATIC_DIR
from nephthys.utils.slack import app as slack_app

req_handler = AsyncSlackRequestHandler(slack_app)


async def endpoint(req: Request):
    return await req_handler.handle(req)


async def health(req: Request):
    try:
        await env.slack_client.api_test()
        slack_healthy = True
    except Exception:
        slack_healthy = False

    try:
        from nephthys.database.tables import User

        await User.raw("SELECT 1")
        db_healthy = True
    except Exception:
        db_healthy = False

    return JSONResponse(
        {
            "healthy": slack_healthy,
            "slack": slack_healthy,
            "database": db_healthy,
        }
    )


async def metrics(req: Request):
    """Prometheus metrics endpoint"""
    main_metrics: bytes = generate_latest()
    return Response(main_metrics, media_type=CONTENT_TYPE_LATEST)


async def root(req: Request):
    return RedirectResponse(url="https://github.com/hackclub/nephthys")


app = Starlette(
    debug=True if env.environment != "production" else False,
    routes=[
        Route(path="/", endpoint=root, methods=["GET"]),
        Route(path="/slack/events", endpoint=endpoint, methods=["POST"]),
        Route(path="/api/stats", endpoint=stats, methods=["GET"]),
        Route(path="/api/stats/range", endpoint=stats_range, methods=["GET"]),
        Route(path="/api/stats_v2", endpoint=stats_v2, methods=["GET"]),
        Route(path="/api/user", endpoint=user_stats, methods=["GET"]),
        Route(path="/api/tickets", endpoint=tickets_list, methods=["GET"]),
        Route(path="/api/ticket", endpoint=ticket_info, methods=["GET"]),
        Route(path="/health", endpoint=health, methods=["GET"]),
        Route(path="/metrics", endpoint=metrics, methods=["GET"]),
        Route(path="/oauth/callback", endpoint=authorize, methods=["GET"]),
        Mount("/public", app=StaticFiles(directory=STATIC_DIR), name="static"),
        Route(path="/lobby", endpoint=lobby, methods=["GET"]),
        Route(path="/lobby/login", endpoint=log_in, methods=["GET"]),
        Route(path="/lobby/logout", endpoint=log_out, methods=["GET"]),
        Route(path="/lobby/api_keys", endpoint=api_keys, methods=["GET"]),
    ],
    lifespan=main,
)

# for HCA OAuth2
app.add_middleware(
    SessionMiddleware,
    secret_key=Secret(secrets.token_urlsafe(32)),
    max_age=365 * 86400,  # 365 days, in seconds
)

app.add_middleware(
    PrometheusMiddleware,
    app_name="nephthys",
    buckets=[
        0.001,
        0.01,
        0.025,
        0.05,
        0.1,
        0.25,
        0.5,
        0.75,
        1.0,
        1.5,
        2.5,
    ],
)
