import logging
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from zoneinfo import ZoneInfo

from nephthys.utils.env import env
from nephthys.utils.logging import send_heartbeat
from nephthys.utils.old_tickets import get_unanswered_tickets
from nephthys.utils.stats import calculate_daily_stats
from nephthys.utils.ticket_methods import get_question_message_link
from nephthys.views.home.components.ticket_status_pie import (
    generate_ticket_status_pie_image,
)
from prisma.models import Ticket


def slack_timestamp(dt: datetime, format: str = "date_short") -> str:
    fallback = dt.isoformat().replace("T", " ")
    return f"<!date^{int(dt.timestamp())}^{{{format}}}|{fallback}>"


async def tickets_awaiting_response_message(tickets: list[Ticket]) -> str:
    if not tickets:
        return ":rac_woah: _btw, i looked for old unanswered tickets, but found none. well done team!_"

    count = len(tickets)
    MAX_TICKETS = 5

    msg_lines = [
        ":rac_shy: *tickets you could take a look at*",
        "i found some older tickets that might be waiting for a response from someone...",
    ]
    for i, ticket in enumerate(tickets[:MAX_TICKETS]):
        label = (
            ticket.title
            or ticket.description[:100]
            or f"Ticket #{ticket.id} (no description)"
        )
        last_reply = (
            slack_timestamp(ticket.lastMsgAt, format="date_short")
            if ticket.lastMsgAt
            else "unknown"
        )
        created_date = slack_timestamp(ticket.createdAt, format="date_short")
        tags = await env.db.tagsontickets.find_many(
            where={"ticketId": ticket.id}, include={"tag": True}
        )
        tags_string = (
            " (" + ", ".join(f"*{t.tag.name}*" for t in tags if t.tag) + ")"
            if tags
            else ""
        )
        msg_lines.append(
            f"{i + 1}. <{get_question_message_link(ticket)}|{label}>{tags_string} (created {created_date}, last reply *{last_reply}*)"
        )
    if count > MAX_TICKETS:
        msg_lines.append(f"_(plus {count - MAX_TICKETS} more)_")

    return "\n".join(msg_lines)


async def send_daily_stats():
    """
    Calculates and sends statistics for the previous day to a Slack channel.
    This task is intended to be run at midnight.
    """
    london_tz = ZoneInfo("Europe/London")
    now_london = datetime.now(london_tz)
    today_midnight_london = now_london.replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    # this gives us the 24-hour period of the previous day
    start_of_yesterday = today_midnight_london - timedelta(days=1)
    end_of_yesterday = today_midnight_london

    logging.info(
        f"Generating daily stats for the period: {start_of_yesterday} to {end_of_yesterday}"
    )

    try:
        stats = await calculate_daily_stats(start_of_yesterday, end_of_yesterday)

        daily_leaderboard_lines = [
            f"{i + 1}. <@{entry['user'].slackId}> - {entry['count']} closed tickets"
            for i, entry in enumerate(stats.helpers_leaderboard[:3])
        ]
        if not daily_leaderboard_lines:
            daily_leaderboard_str = "_No tickets were closed yesterday!_"
        else:
            daily_leaderboard_str = "\n".join(daily_leaderboard_lines)

        tickets_awaiting_response = await get_unanswered_tickets(
            since=today_midnight_london - timedelta(days=5)
        )

        pie_chart = await generate_ticket_status_pie_image(
            tz=timezone(now_london.utcoffset() or timedelta(0))
        )

        msg = f"""
um, um, hi there! hope i'm not disturbing you, but i just wanted to let you know that i've got some stats for you! :rac_cute:

*:mc-clock: in the last 24 hours...* _(that's a day, right? right? that's a day, yeah ok)_
:rac_woah: *{stats.new_tickets_total}* total tickets were opened and you managed to close *{stats.closed_today_from_today}* of them! congrats!! :D
:rac_info: *{stats.assigned_today_in_progress}* tickets have been assigned to users, and *{stats.new_tickets_still_open}* are still open
you managed to close a whopping *{stats.closed_today}* tickets in the last 24 hours, well done!

*:rac_info: today's leaderboard*
{daily_leaderboard_str}

{await tickets_awaiting_response_message(tickets_awaiting_response)}
"""

        await env.slack_client.files_upload_v2(
            channel=env.slack_bts_channel,
            file=pie_chart,  # type: ignore (we requested a raw pie chart so type is bytes)
            title="ticket status",
            initial_comment=msg,
        )

        logging.info("Daily stats message sent successfully.")

    except Exception as e:
        logging.error(f"Failed to send daily stats: {e}", exc_info=True)
        try:
            await send_heartbeat(
                "Failed to send daily stats",
                messages=[str(e)],
            )
        except Exception as slack_e:
            logging.error(
                f"Could not send error notification to Slack maintainer: {slack_e}"
            )
