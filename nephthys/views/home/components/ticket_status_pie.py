from datetime import datetime
from datetime import timedelta
from datetime import timezone
from io import BytesIO

import numpy as np
from blockkit import Image

from nephthys.utils.bucky import upload_file
from nephthys.utils.env import env
from nephthys.utils.graphs.pie import generate_pie_chart
from nephthys.utils.performance import perf_timer
from nephthys.utils.time import is_day
from prisma.enums import TicketStatus

LAST_DAYS = 7


async def generate_ticket_status_pie_image(tz: timezone | None = None) -> bytes:
    """Generates a pie chart showing percentages of open/closed/in progress
    tickets over the last 7 days, renders it as a PNG and returns it as bytes."""
    is_daytime = is_day(tz) if tz else True

    if is_daytime:
        text_colour = "black"
        bg_colour = "white"
    else:
        text_colour = "white"
        bg_colour = "#181A1E"

    now = datetime.now(timezone.utc)
    one_week_ago = now - timedelta(days=LAST_DAYS)

    async with perf_timer("Fetching ticket counts from DB"):
        recently_closed_tickets = await env.db.ticket.count(
            where={
                "status": TicketStatus.CLOSED,
                "closedAt": {"gte": one_week_ago},
            }
        )
        in_progress_tickets = await env.db.ticket.count(
            where={"status": TicketStatus.IN_PROGRESS}
        )
        open_tickets = await env.db.ticket.count(where={"status": TicketStatus.OPEN})

    y = [recently_closed_tickets, in_progress_tickets, open_tickets]
    labels = ["Closed", "In Progress", "Open"]
    colours = [
        "#80EF80",
        "#FFEE8C",
        "#FF746C",
    ]

    async with perf_timer("Building pie chart"):
        for count in range(
            len(y) - 1, -1, -1
        ):  # iterate in reverse so that indexes are not affected
            if y[count] == 0:
                del y[count]
                del labels[count]
                del colours[count]

        b = BytesIO()
        y = np.array(y)
        plt = generate_pie_chart(
            y=y,
            labels=labels,
            colours=colours,
            text_colour=text_colour,
            bg_colour=bg_colour,
        )
    async with perf_timer("Saving pie chart to buffer"):
        plt.savefig(
            b,
            bbox_inches="tight",
            pad_inches=0.1,
            transparent=False,
            dpi=300,
            format="png",
        )

    return b.getvalue()


async def ticket_status_pie_chart_component(tz: timezone | None = None):
    pie_chart_image = await generate_ticket_status_pie_image(tz)

    async with perf_timer("Uploading pie chart"):
        url = await upload_file(
            file=pie_chart_image,
            filename="ticket_status.png",
            content_type="image/png",
        )

    if not url:
        return Image(
            image_url=f"{env.base_url}/public/binoculars.png",
            alt_text="Heidi looking for tickets with binoculars",
            title="looks like heidi's scrounging around for tickets in the trash",
        )

    return Image(
        image_url=url,
        alt_text="Ticket Stats",
        title=f"Ticket stats (last {LAST_DAYS} days)",
    )
