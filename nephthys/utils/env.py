import logging
import os
from typing import Literal

from aiohttp import ClientSession
from dotenv import load_dotenv
from openai import AsyncOpenAI
from slack_sdk.web.async_client import AsyncWebClient

from nephthys.transcripts import transcripts
from nephthys.transcripts.transcript import Transcript
from prisma import Prisma

load_dotenv(override=True)


class Environment:
    def __init__(self):
        self.slack_bot_token = os.environ.get("SLACK_BOT_TOKEN", "unset")
        self.slack_user_token = os.environ.get("SLACK_USER_TOKEN", "unset")
        self.slack_signing_secret = os.environ.get("SLACK_SIGNING_SECRET", "unset")
        self.slack_app_token = os.environ.get("SLACK_APP_TOKEN")

        self.uptime_url = os.environ.get("UPTIME_URL")
        self.site_url = os.environ.get("SITE_URL", "https://summer.hackclub.com")
        self.site_api_key = os.environ.get("SITE_API_KEY", "unset")
        self.hack_club_ai_api_key = os.environ.get("HACK_CLUB_AI_API_KEY")

        self.environment = os.environ.get("ENVIRONMENT", "development")
        self.log_level = os.environ.get(
            "LOG_LEVEL",
            logging.WARNING if self.environment == "production" else logging.INFO,
        )

        self.slack_help_channel = os.environ.get("SLACK_HELP_CHANNEL", "unset")
        self.slack_ticket_channel = os.environ.get("SLACK_TICKET_CHANNEL", "unset")
        self.slack_bts_channel = os.environ.get("SLACK_BTS_CHANNEL", "unset")
        self.slack_user_group = os.environ.get("SLACK_USER_GROUP", "unset")
        self.slack_maintainer_id = os.environ.get("SLACK_MAINTAINER_ID", "unset")
        self.program = os.environ.get("PROGRAM", "summer_of_making")
        self.daily_summary = True if not os.environ.get("DAILY_SUMMARY") else False
        self.app_title = os.environ.get("APP_TITLE", "helper heidi")

        self.port = int(os.environ.get("PORT", 3000))

        self.slack_heartbeat_channel = os.environ.get("SLACK_HEARTBEAT_CHANNEL")

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
        self.db = Prisma()
        self.transcript = next(
            (
                program
                for program in transcript_instances
                if program.program_snake_case == self.program
            ),
            Transcript(),
        )

        self.slack_client = AsyncWebClient(token=self.slack_bot_token)
        self.ai_client = (
            AsyncOpenAI(
                base_url="https://ai.hackclub.com/proxy/v1",
                api_key=self.hack_club_ai_api_key,
            )
            if self.hack_club_ai_api_key
            else None
        )

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
