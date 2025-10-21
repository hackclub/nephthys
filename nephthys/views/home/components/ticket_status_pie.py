import logging
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from io import BytesIO
from time import perf_counter

import numpy as np

from nephthys.utils.bucky import upload_file
from nephthys.utils.env import env
from nephthys.utils.graphs.pie import generate_pie_chart
from nephthys.utils.time import is_day
from prisma.enums import TicketStatus


async def get_ticket_status_pie_chart(
    tz: timezone | None = None, raw: bool = False
) -> dict | bytes:
    time_start = perf_counter()
    is_daytime = is_day(tz) if tz else True

    if is_daytime:
        text_colour = "black"
        bg_colour = "white"
    else:
        text_colour = "white"
        bg_colour = "#181A1E"

    now = datetime.now(timezone.utc)
    one_week_ago = now - timedelta(days=7)

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
    time_get_tickets = perf_counter()
    logging.debug(f"Fetched tickets in {time_get_tickets - time_start:.4f} seconds")

    y = [recently_closed_tickets, in_progress_tickets, open_tickets]
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
    time_generate_chart = perf_counter()
    logging.debug(
        f"Built pie chart in {time_generate_chart - time_get_tickets:.4f} seconds"
    )
    plt.savefig(
        b, bbox_inches="tight", pad_inches=0.1, transparent=False, dpi=300, format="png"
    )
    time_save_chart = perf_counter()
    logging.debug(
        f"Saved pie chart to buffer in {time_save_chart - time_generate_chart:.4f} seconds"
    )

    plt.show()

    if raw:
        return b.getvalue()

    url = await upload_file(
        file=b.getvalue(),
        filename="ticket_status.png",
        content_type="image/png",
    )
    time_upload_file = perf_counter()
    logging.debug(
        f"Uploaded pie chart in {time_upload_file - time_save_chart:.4f} seconds"
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
