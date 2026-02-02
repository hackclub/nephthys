from pathlib import Path

from prometheus_client import CONTENT_TYPE_LATEST
from prometheus_client import generate_latest
from slack_bolt.adapter.starlette.async_handler import AsyncSlackRequestHandler
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.responses import RedirectResponse
from starlette.responses import Response
from starlette.routing import Mount
from starlette.routing import Route
from starlette.staticfiles import StaticFiles
from starlette_exporter import PrometheusMiddleware

from nephthys.__main__ import main
from nephthys.api.stats import stats
from nephthys.api.stats_v2 import stats_v2
from nephthys.api.ticket import ticket_info
from nephthys.api.user import user_stats
from nephthys.utils.env import env
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

    db_healthy = env.db.is_connected()

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
    prisma_metrics = await env.db.get_metrics(format="prometheus")
    all_metrics = main_metrics + prisma_metrics.encode("utf-8")
    return Response(all_metrics, media_type=CONTENT_TYPE_LATEST)


async def root(req: Request):
    return RedirectResponse(url="https://github.com/hackclub/nephthys")


STATIC_DIR = Path(Path.cwd() / "nephthys" / "public")

app = Starlette(
    debug=True if env.environment != "production" else False,
    routes=[
        Route(path="/", endpoint=root, methods=["GET"]),
        Route(path="/slack/events", endpoint=endpoint, methods=["POST"]),
        Route(path="/api/stats", endpoint=stats, methods=["GET"]),
        Route(path="/api/stats_v2", endpoint=stats_v2, methods=["GET"]),
        Route(path="/api/user", endpoint=user_stats, methods=["GET"]),
        Route(path="/api/ticket", endpoint=ticket_info, methods=["GET"]),
        Route(path="/health", endpoint=health, methods=["GET"]),
        Route(path="/metrics", endpoint=metrics, methods=["GET"]),
        Mount("/public", app=StaticFiles(directory=STATIC_DIR), name="static"),
    ],
    lifespan=main,
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
