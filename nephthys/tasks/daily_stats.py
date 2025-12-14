import logging
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from zoneinfo import ZoneInfo

from nephthys.utils.env import env
from nephthys.utils.logging import send_heartbeat
from nephthys.utils.stats import calculate_daily_stats
from nephthys.views.home.components.ticket_status_pie import get_ticket_status_pie_chart


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

        pie_chart = await get_ticket_status_pie_chart(
            raw=True, tz=timezone(now_london.utcoffset() or timedelta(0))
        )

        msg = f"""
um, um, hi there! hope i'm not disturbing you, but i just wanted to let you know that i've got some stats for you! :rac_cute:

*:mc-clock: in the last 24 hours...* _(that's a day, right? right? that's a day, yeah ok)_
:rac_woah: *{stats.new_tickets_total}* total tickets were opened and you managed to close *{stats.closed_today_from_today}* of them! congrats!! :D
:rac_info: *{stats.assigned_today_in_progress}* tickets have been assigned to users, and *{stats.new_tickets_still_open}* are still open
you managed to close a whopping *{stats.new_tickets_now_closed}* tickets in the last 24 hours, well done!

*:rac_shy: today's leaderboard*
{daily_leaderboard_str}
"""

        await env.slack_client.files_upload_v2(
            channel=env.slack_bts_channel,
            file=pie_chart,
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
