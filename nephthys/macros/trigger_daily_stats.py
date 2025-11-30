from nephthys.macros.types import Macro
from nephthys.tasks import daily_stats
from nephthys.utils.env import env


class DailyStats(Macro):
    name = "dailystats"
    can_run_on_closed = True

    async def run(self, ticket, helper, **kwargs):
        """Development-only macro to manually trigger the daily summary message"""
        if not env.environment == "development":
            await env.slack_client.chat_postEphemeral(
                channel=env.slack_help_channel,
                thread_ts=ticket.msgTs,
                user=helper.slackId,
                text="The `dailystats` macro can only be run in development environments.",
            )
            return
        await daily_stats.send_daily_stats()
