import logging
from datetime import datetime
from datetime import timedelta

from nephthys.database.tables import CategoryTag
from nephthys.database.tables import TagsOnTickets
from nephthys.database.tables import Ticket
from nephthys.database.tables import TicketStatus
from nephthys.utils.env import env
from nephthys.utils.logging import send_heartbeat
from nephthys.utils.ticket_methods import get_question_message_link


def slack_timestamp(dt: datetime, format: str = "date_short") -> str:
    fallback = dt.isoformat().replace("T", " ")
    return f"<!date^{int(dt.timestamp())}^{{{format}}}|{fallback}>"


async def send_fulfillment_reminder():
    """
    Checks for 'Shop/fulfillment query' tag and sends a reminder with open tickets for the fulfillment team/amber
    Run daily at 2 PM (London Time)
    """

    target_tag_name = "Shop/fulfillment query"
    target_slack_id = "U054VC2KM9P"

    logging.info("Running fulfillment team reminder task")

    try:
        tag = (
            await CategoryTag.objects()
            .where(CategoryTag.name == target_tag_name)
            .first()
        )

        if not tag:
            logging.info(
                f"Tag '{target_tag_name}' not found. Skipping fulfillment reminder."
            )
            return

        now = datetime.now()
        twenty_four_hours_ago = now - timedelta(hours=24)

        tickets = await Ticket.objects(Ticket.opened_by).where(
            (Ticket.category_tag == tag.id)
            & (Ticket.status.is_in([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]))
            & (Ticket.created_at >= twenty_four_hours_ago)
        )

        msg_header = f"oh hi <@{target_slack_id}>! i found some fulfillment tickets for you! :rac_cute:"

        if not tickets:
            logging.info("No open fulfillment tickets found. Skipping Slack reminder.")
            return

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
                created_ts = slack_timestamp(ticket.created_at, format="date_short")

                tag_links = await TagsOnTickets.objects(TagsOnTickets.tag).where(
                    TagsOnTickets.ticket == ticket.id
                )
                tags_string = (
                    " ("
                    + ", ".join(f"*{t.tag.name}*" for t in tag_links if t.tag)
                    + ")"
                    if tag_links
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
