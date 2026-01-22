from datetime import datetime
from datetime import timedelta
from datetime import timezone
from io import BytesIO

import numpy as np

from nephthys.utils.bucky import upload_file
from nephthys.utils.env import env
from nephthys.utils.graphs.pie import generate_pie_chart
from nephthys.utils.performance import perf_timer
from nephthys.utils.time import is_day
from prisma.enums import TicketStatus


async def get_ticket_status_pie_chart(
    tz: timezone | None = None, raw: bool = False
) -> dict | bytes:
    is_daytime = is_day(tz) if tz else True

    if is_daytime:
        text_colour = "black"
        bg_colour = "white"
    else:
        text_colour = "white"
        bg_colour = "#181A1E"

    now = datetime.now(timezone.utc)
    one_week_ago = now - timedelta(days=7)

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

    if raw:
        return b.getvalue()

    async with perf_timer("Uploading pie chart"):
        url = await upload_file(
            file=b.getvalue(),
            filename="ticket_status.png",
            content_type="image/png",
        )

    caption = "Ticket stats"

    if not url:
        url = f"{env.hostname}/public/binoculars.png"
        caption = "looks like heidi's scrounging around for tickets in the trash"

    return {
        "type": "image",
        "title": {
            "type": "plain_text",
            "text": caption,
            "emoji": True,
        },
        "image_url": url,
        "alt_text": "Ticket Stats",
    }
