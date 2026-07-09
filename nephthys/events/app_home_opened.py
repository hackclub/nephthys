import logging
import traceback
from dataclasses import dataclass
from typing import Any

from prometheus_client import Histogram
from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.database.tables import User
from nephthys.utils.env import env
from nephthys.utils.logging import send_heartbeat
from nephthys.utils.performance import perf_timer
from nephthys.views.home import AppHomeView
from nephthys.views.home.assigned import get_assigned_tickets_view
from nephthys.views.home.category_tags import get_category_tags_view
from nephthys.views.home.dashboard import get_dashboard_view
from nephthys.views.home.error import get_error_view
from nephthys.views.home.loading import get_loading_view
from nephthys.views.home.stats import get_stats_view
from nephthys.views.home.team_tags import get_team_tags_view


@dataclass
class RequestedView:
    home_type: AppHomeView
    page: int | None = None


DEFAULT_VIEW = AppHomeView.DASHBOARD


async def on_app_home_opened(event: dict[str, Any], client: AsyncWebClient):
    slack_id = event["user"]
    user = await User.objects().get(User.slack_id == slack_id)
    # Restore the the last view the user had open, if any
    if user and user.app_home_last_view:
        try:
            initial_view = AppHomeView(user.app_home_last_view)
            logging.info(
                f"Restoring saved app home view slack_id={slack_id} view={initial_view}"
            )
        except ValueError:
            logging.error(
                f"Invalid app_home_last_view in DB for user_id={user.id} last_view={user.app_home_last_view}"
            )
            initial_view = DEFAULT_VIEW
    else:
        initial_view = DEFAULT_VIEW
    await open_app_home(initial_view, client, slack_id)


APP_HOME_RENDER_DURATION = Histogram(
    "nephthys_app_home_render_duration_seconds",
    "How long it takes to load the app home screen",
    ["home_type"],
)


# Map of the last-requested view for each Slack user
# This prevents a view that took a while to render overwriting the view you want
# Entries are deleted once the view is published
last_requested_views: dict[str, RequestedView] = {}


async def open_app_home(
    home_type: AppHomeView,
    client: AsyncWebClient,
    user_id: str,
    page: int | None = None,
):
    last_requested_views[user_id] = RequestedView(home_type, page)
    try:
        await client.views_publish(view=get_loading_view(home_type), user_id=user_id)

        # Generate the view (this is when DB queries are made)
        user = await User.objects().where(User.slack_id == user_id).first()
        logging.info(f"Opening {home_type} for {user_id}")

        async with perf_timer(
            f"Rendering app home (type={home_type})",
            APP_HOME_RENDER_DURATION,
            home_type=home_type,
        ):
            match home_type:
                case AppHomeView.DASHBOARD:
                    view = await get_dashboard_view(slack_user=user_id, db_user=user)
                case AppHomeView.ASSIGNED_TICKETS:
                    view = await get_assigned_tickets_view(user, page=page or 1)
                case AppHomeView.TEAM_TAGS:
                    view = await get_team_tags_view(user)
                case AppHomeView.CATEGORY_TAGS:
                    view = await get_category_tags_view(user)
                case AppHomeView.MY_STATS:
                    view = await get_stats_view(user)

        # Check that the request hasn't been superseded by another request while we were rendering
        user_last_requested_view = last_requested_views.get(user_id)
        if user_last_requested_view:
            if user_last_requested_view != RequestedView(home_type, page):
                logging.info(
                    f"Ignoring stale view request slack_id={user_id} view={home_type} page={page}"
                )
                return
            del last_requested_views[user_id]

        # Publish the view!
        await publish_view(client, user_id, view)

        # Record the user's last-viewed page for future visits
        if user:
            user.app_home_last_view = home_type.value
            await user.save()

    except Exception as e:
        logging.error(f"Error opening app home: {e}")
        tb = traceback.format_exception(e)

        tb_str = "".join(tb)

        view = get_error_view(
            f"An error occurred while opening the app home: {e}",
            traceback=tb_str,
        )
        err_type = type(e).__name__
        await send_heartbeat(
            f"`{err_type}` opening app home for <@{user_id}>",
            messages=[f"```{tb_str}```", f"cc <@{env.slack_maintainer_id}>"],
        )
        await publish_view(client, user_id, view)


async def publish_view(client: AsyncWebClient, user_id: str, view: dict[str, Any]):
    try:
        await client.views_publish(user_id=user_id, view=view)
    except SlackApiError as e:
        logging.error(f"Error publishing app home view: {e}")
        await client.views_publish(
            user_id=user_id,
            view=get_error_view(
                f"A Slack API error occurred while opening the app home:\n{e}",
            ),
        )
