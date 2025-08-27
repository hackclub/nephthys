from datetime import datetime
from datetime import timedelta
from datetime import timezone
from io import BytesIO

import numpy as np

from nephthys.utils.env import env
from nephthys.utils.graphs.pie import generate_pie_chart
from nephthys.utils.litterbox import upload_litter
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

    status_counts = {
        TicketStatus.CLOSED: 0,
        TicketStatus.IN_PROGRESS: 0,
        TicketStatus.OPEN: 0,
    }

    tickets = await env.db.ticket.find_many() or []

    now = datetime.now(timezone.utc)
    one_week_ago = now - timedelta(days=7)

    for ticket in tickets:
        if ticket.status == TicketStatus.CLOSED:
            # Only count closed tickets resolved in the last week
            if (
                hasattr(ticket, "closedAt")
                and ticket.closedAt
                and ticket.closedAt >= one_week_ago
            ):
                status_counts[TicketStatus.CLOSED] += 1
        elif ticket.status == TicketStatus.IN_PROGRESS:
            status_counts[TicketStatus.IN_PROGRESS] += 1
        elif ticket.status == TicketStatus.OPEN:
            status_counts[TicketStatus.OPEN] += 1

    y = [count for count in status_counts.values()]
    labels = ["Closed", "In Progress", "Open"]
    colours = [
        "#80EF80",
        "#FFEE8C",
        "#FF746C",
    ]

    for count in range(
        len(y) - 1, -1, -1
    ):  # iterate in reverse so that indexes are not affected
        if y[count] == 0:
            del y[count]
            del labels[count]
            del colours[count]

    y = np.array(y)

    b = BytesIO()
    plt = generate_pie_chart(
        y=y,
        labels=labels,
        colours=colours,
        text_colour=text_colour,
        bg_colour=bg_colour,
    )
    plt.savefig(
        b, bbox_inches="tight", pad_inches=0.1, transparent=False, dpi=300, format="png"
    )

    if raw:
        return b.getvalue()

    url = await upload_litter(
        file=b.getvalue(),
        filename="ticket_status.png",
        expiry="1h",
        content_type="image/png",
    )
    caption = "Ticket stats"

    if not url:
        url = "https://hc-cdn.hel1.your-objectstorage.com/s/v3/888f292372d8450449b41dd18767812c72518449_binoculars.png"
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
