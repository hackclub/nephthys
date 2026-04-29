from slack_sdk.errors import SlackApiError

from nephthys.actions.resolve import resolve
from nephthys.database.enums import TicketStatus
from nephthys.database.tables import User
from nephthys.macros.types import Macro
from nephthys.utils.env import env
from nephthys.utils.ticket_methods import delete_bot_replies


class Thread(Macro):
    name = "thread"
    can_run_on_closed = True

    async def run(self, ticket, helper, **kwargs):
        """
        A macro that deletes the Nephthys message and removes the
        reaction to avoid duplicate thread clutter
        """
        sender = await User.objects().where(User.id == ticket.opened_by).first()
        if not sender:
            return

        # Deletes the first (FAQ) message sent by the bot
        await delete_bot_replies(ticket.id)

        if ticket.status != TicketStatus.CLOSED:
            await resolve(
                ts=ticket.msg_ts,
                resolver=helper.slack_id,
                client=env.slack_client,
                add_reaction=False,
                send_resolved_message=False,
            )
            return

        # If the ticket was already closed, now we just need to remove any reactions
        try:
            reactions = ["thinking_face", "white_check_mark"]
            for reaction in reactions:
                await env.slack_client.reactions_remove(
                    channel=env.slack_help_channel,
                    timestamp=ticket.msg_ts,
                    name=reaction,
                )
        except SlackApiError as e:
            if e.response["error"] != "no_reaction":
                raise e
