import logging
import os
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from typing import overload

from aiohttp import ClientSession
from dotenv import load_dotenv
from slack_sdk.web.async_client import AsyncWebClient
from starlette.datastructures import Secret

from nephthys.transcripts import transcripts
from nephthys.transcripts.transcript import Transcript

# Static paths
STATIC_DIR = Path(Path.cwd() / "nephthys" / "public")
TEMPLATES_DIR = Path(Path.cwd() / "nephthys" / "templates")

load_dotenv(override=True)


@overload
def get_environ[T: str](key: str, default: T) -> str | T: ...
@overload
def get_environ(key: str, default: None = None) -> str | None: ...
def get_environ(key: str, default: str | None = None) -> str | None:
    return os.environ.get(key, default)


def get_environ_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name, None)
    if value is None:
        return default
    value = value.strip().lower()
    if value in {"1", "true", "t", "yes", "y", "on"}:
        return True
    if value in {"0", "false", "f", "no", "n", "off"}:
        return False
    raise ValueError(f"Invalid boolean env var {name}={value!r}")


@dataclass
class HCAConfig:
    client_id: str
    client_secret: str
    base_url: str
    session_secret: Secret


def create_hca_config(environment: str) -> HCAConfig | None:
    hca_client_id = os.environ.get("HCA_CLIENT_ID")
    hca_client_secret = os.environ.get("HCA_CLIENT_SECRET")
    session_secret = os.environ.get("SESSION_SECRET")
    if (not hca_client_id) and (not hca_client_secret):
        return None
    if (not hca_client_id) or (not hca_client_secret):
        raise ValueError(
            "Both of HCA_CLIENT_ID and HCA_CLIENT_SECRET must be set; or neither must be set (for no HCA integration)"
        )
    if not session_secret:
        if environment != "development":
            raise ValueError(
                "SESSION_SECRET environment variable must be set when HCA integration is enabled"
            )
        logging.info(
            "Generating random session signing secret for development (set SESSION_SECRET to persist sessions)"
        )
        session_secret = secrets.token_urlsafe(32)

    return HCAConfig(
        client_id=hca_client_id,
        client_secret=hca_client_secret,
        base_url=os.environ.get("HCA_BASE_URL", "https://auth.hackclub.com"),
        session_secret=Secret(session_secret),
    )


def get_base_url() -> str:
    if base_url := os.environ.get("BASE_URL"):
        return base_url.rstrip("/")
    if coolify_url := os.environ.get("COOLIFY_URL"):
        logging.info(f"Using base URL from Coolify: base_url={coolify_url}")
        return coolify_url.rstrip("/")
    # Falling back to this means that it'll use assets served by nephthys.hackclub.com, which does work
    FALLBACK_URL = "https://nephthys.hackclub.com"
    logging.warning(f"Using fallback base_url={FALLBACK_URL}")
    return FALLBACK_URL.rstrip("/")


class Environment:
    def __init__(self):
        self.slack_bot_token = os.environ.get("SLACK_BOT_TOKEN", "unset")
        self.slack_user_token = os.environ.get("SLACK_USER_TOKEN", "unset")
        self.slack_signing_secret = os.environ.get("SLACK_SIGNING_SECRET", "unset")
        self.slack_app_token = os.environ.get("SLACK_APP_TOKEN")

        self.uptime_url = os.environ.get("UPTIME_URL")
        self.ai_title_model = os.environ.get("AI_TITLE_MODEL", "openai/gpt-oss-120b")
        self.ai_category_model = os.environ.get(
            "AI_CATEGORY_MODEL", "typesafe/jev-1.13"
        )

        self.otel_logs_url = os.environ.get("OTEL_EXPORTER_OTLP_LOGS_ENDPOINT")
        self.otel_service_name = os.environ.get("OTEL_SERVICE_NAME", "nephthys")
        # Allows easily providing HTTP Basic Auth credentials formatted as user:pass
        self.otel_logs_basic_auth = os.environ.get("OTEL_EXPORTER_OTLP_LOGS_BASIC_AUTH")

        self.environment = os.environ.get("ENVIRONMENT", "development")
        default_log_level = (
            logging.WARNING if self.environment == "production" else logging.INFO
        )
        self.log_level_stderr = (
            os.environ.get("LOG_LEVEL_STDERR")
            or os.environ.get("LOG_LEVEL")
            or default_log_level
        )
        self.log_level_otel = os.environ.get("LOG_LEVEL_OTEL", logging.INFO)
        self.base_url: str = get_base_url()

        self.slack_help_channel = os.environ.get("SLACK_HELP_CHANNEL", "unset")
        self.slack_ticket_channel = os.environ.get("SLACK_TICKET_CHANNEL", "unset")
        self.slack_bts_channel = os.environ.get("SLACK_BTS_CHANNEL", "unset")
        self.slack_maintainer_id = os.environ.get("SLACK_MAINTAINER_ID", "unset")
        self.program = os.environ.get("PROGRAM", "summer_of_making")
        self.daily_summary = get_environ_bool("DAILY_SUMMARY", default=True)
        self.enable_feedback = get_environ_bool("ENABLE_FEEDBACK", default=False)
        self.app_title = os.environ.get("APP_TITLE", "helper heidi")
        self.hca = create_hca_config(self.environment)

        self.port = int(os.environ.get("PORT", 3000))

        self.slack_heartbeat_channel = os.environ.get("SLACK_HEARTBEAT_CHANNEL")

        # Stale ticket auto-close: number of days of inactivity before closing
        # Set to a positive integer to enable, leave unset to disable
        stale_days_str = os.environ.get("STALE_TICKET_DAYS")
        if stale_days_str:
            try:
                stale_days = int(stale_days_str)
                self.stale_ticket_days = stale_days if stale_days > 0 else None
                if stale_days <= 0:
                    logging.warning(
                        f"STALE_TICKET_DAYS must be positive, got {stale_days}. Disabling."
                    )
            except ValueError:
                logging.warning(
                    f"Invalid STALE_TICKET_DAYS value: {stale_days_str}. Disabling."
                )
                self.stale_ticket_days = None
        else:
            self.stale_ticket_days = None

        unset = [key for key, value in self.__dict__.items() if value == "unset"]

        if unset:
            raise ValueError(f"Missing environment variables: {', '.join(unset)}")

        transcript_instances = [program() for program in transcripts]
        valid_programs = [
            program.program_snake_case for program in transcript_instances
        ]
        if self.program not in valid_programs:
            raise ValueError(
                f"Invalid PROGRAM environment variable: {self.program}. "
                f"Must be one of {valid_programs}"
            )

        self.session: ClientSession
        self.transcript = next(
            (
                program
                for program in transcript_instances
                if program.program_snake_case == self.program
            ),
            Transcript(),
        )

        self.slack_client = AsyncWebClient(token=self.slack_bot_token)

        # Cache whether the user token has workspace admin privileges
        self._workspace_admin_available: bool | Literal["unchecked"] = "unchecked"

    async def workspace_admin_available(self) -> bool:
        """Check if the provided user token has workspace admin privileges."""
        if self._workspace_admin_available != "unchecked":
            return self._workspace_admin_available
        user_token_identity = await self.slack_client.auth_test(
            token=self.slack_user_token
        )
        user_id = user_token_identity["user_id"]
        if not user_id:
            raise ValueError(
                f"Unable to get my user ID from Slack API: {user_token_identity}"
            )
        user_info_response = await self.slack_client.users_info(user=user_id)
        user_info = user_info_response["user"]
        if not user_info:
            raise ValueError("Failed to get user info from Slack API.")
        self._workspace_admin_available = user_info["is_admin"]
        return user_info["is_admin"]


env = Environment()
