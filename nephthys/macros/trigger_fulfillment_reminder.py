from nephthys.macros.types import Macro
from nephthys.tasks import fulfillment_reminder
from nephthys.utils.env import env


class FulfillmentReminder(Macro):
    name = "fulfillment_reminder"
    can_run_on_closed = True

    async def run(self, ticket, helper, **kwargs):
        """Development-only macro to manually trigger the fulfillment reminder message"""
        if not env.environment == "development":
            await env.slack_client.chat_postEphemeral(
                channel=env.slack_help_channel,
                thread_ts=ticket.msgTs,
                user=helper.slackId,
                text="The `fulfillment_reminder` macro can only be run in development environments.",
            )
            return
        await fulfillment_reminder.send_fulfillment_reminder()
