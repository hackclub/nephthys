import logging
from base64 import b64encode
from os import uname
from uuid import uuid4

from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs import LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource

from nephthys.utils.env import env


async def send_heartbeat(heartbeat: str, messages: list[str] = []):
    if env.slack_heartbeat_channel:
        msg = await env.slack_client.chat_postMessage(
            channel=env.slack_heartbeat_channel, text=heartbeat
        )
        if messages:
            for message in messages:
                await env.slack_client.chat_postMessage(
                    channel=env.slack_heartbeat_channel,
                    text=message,
                    thread_ts=msg["ts"],
                )


def parse_level_name(level_name: str | int) -> int:
    if isinstance(level_name, int):
        return level_name
    name = level_name.upper()
    if name == "VERBOSE":
        name = "DEBUG"
    name_to_int = logging.getLevelNamesMapping()
    try:
        return name_to_int[name]
    except KeyError:
        raise ValueError(f"Invalid log level: {level_name}")


def setup_otel_logging():
    """Set up OpenTelemetry logging, using env vars for configuration."""
    provider = LoggerProvider(
        resource=Resource.create(
            {
                "service.name": env.otel_service_name,
                "service.instance.id": uuid4().hex,
                "deployment.environment": env.environment,
                "host.name": uname().nodename,
            }
        ),
    )
    set_logger_provider(provider)

    auth_header = (
        "Basic " + b64encode(env.otel_logs_basic_auth.encode()).decode()
        if env.otel_logs_basic_auth
        else None
    )
    otlp_exporter = OTLPLogExporter(
        endpoint=env.otel_logs_url,
        headers={"Authorization": auth_header} if auth_header else {},
    )
    provider.add_log_record_processor(BatchLogRecordProcessor(otlp_exporter))

    # Don't allow DEBUG logs to be sent via HTTP, because that creates infinite recursive HTTP request logs
    log_level = max(parse_level_name(env.log_level_otel), logging.INFO)
    handler = LoggingHandler(level=log_level, logger_provider=provider)

    logging.getLogger().addHandler(handler)
    logging.info("Initialised OpenTelemetry logs exporter from environment variables")
