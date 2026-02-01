import logging
from datetime import datetime
from datetime import timedelta

from nephthys.utils.env import env
from nephthys.utils.logging import send_heartbeat
from nephthys.utils.ticket_methods import get_question_message_link
from prisma.enums import TicketStatus


def slack_timestamp(dt: datetime, format: str = "date_short") -> str:
    fallback = dt.isoformat().replace("T", " ")
    return f"<!date^{int(dt.timestamp())}^{{{format}}}|{fallback}>"


async def send_fulfillment_reminder():
    """
    Checks for 'Shop/fulfillment query' tag and sends a reminder with open tickets for the fulfillment team/amber
    Run daily at 2 PM EST
    """

    target_tag_name = "Shop/fulfillment query"
    target_slack_id = "U054VC2KM9P"

    logging.info("Running fulfillment team reminder task")

    try:
        tag = await env.db.categorytag.find_unique(where={"name": target_tag_name})

        if not tag:
            logging.info(
                f"Tag '{target_tag_name}' not found. Skipping fulfillment reminder."
            )
            return

        now = datetime.now()
        twenty_four_hours_ago = now - timedelta(hours=24)

        tickets = await env.db.ticket.find_many(
            where={
                "categoryTagId": tag.id,
                "status": {"in": [TicketStatus.OPEN, TicketStatus.IN_PROGRESS]},
                "createdAt": {"gte": twenty_four_hours_ago},
            },
            include={"openedBy": True, "tagsOnTickets": {"include": {"tag": True}}},
        )

        msg_header = f"oh hi <@{target_slack_id}>! i found some fulfillment tickets for you! :rac_cute:"

        if not tickets:
            msg_body = "_no new open fulfillment tickets in the last 24 hours! nice!_"
        else:
            msg_lines = [
                f":rac_shy: *tickets needing attention ({len(tickets)})*",
                "here are the open tickets from the last 24 hours:",
            ]

            for i, ticket in enumerate(tickets):
                label = (
                    ticket.title or ticket.description[:100] or f"Ticket #{ticket.id}"
                )

                link = get_question_message_link(ticket)
                created_ts = slack_timestamp(ticket.createdAt, format="date_short")

                tags = ticket.tagsOnTickets
                tags_string = (
                    " (" + ", ".join(f"*{t.tag.name}*" for t in tags if t.tag) + ")"
                    if tags
                    else ""
                )

                msg_lines.append(
                    f"{i + 1}. <{link}|{label}>{tags_string} (created {created_ts})"
                )

            msg_body = "\n".join(msg_lines)

        full_msg = f"""
{msg_header}

{msg_body}
"""

        await env.slack_client.chat_postMessage(
            channel=env.slack_bts_channel,
            text=f"Reminder for <@{target_slack_id}>",
            blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": full_msg}}],
        )

        logging.info("Fulfillment reminder sent successfully.")

    except Exception as e:
        logging.error(f"Failed to send fulfillment reminder: {e}", exc_info=True)
        try:
            await send_heartbeat(
                "Failed to send fulfillment reminder",
                messages=[str(e)],
            )
        except Exception as slack_e:
            logging.error(
                f"Could not send error notification to Slack maintainer: {slack_e}"
            )
