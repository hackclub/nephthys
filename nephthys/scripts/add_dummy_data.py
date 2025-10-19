import asyncio
import logging
from datetime import datetime
from datetime import timedelta
from random import randint
from sys import argv

from nephthys.utils.env import env
from nephthys.utils.logging import send_heartbeat
from prisma.enums import TicketStatus


async def create_dummy_records(num_records: int):
    await env.db.connect()
    # We generate random timestamps from up to 3 months ago
    timestamp_a = datetime.now() - timedelta(days=90)
    timestamp_b = datetime.now()
    timestamp_range = (int(timestamp_a.timestamp()), int(timestamp_b.timestamp()))
    for i in range(num_records):
        timestamp = randint(*timestamp_range)
        await env.db.ticket.create(
            {
                "title": f"Test ticket {i}",
                "description": f"Test ticket number {i}",
                "msgTs": f"{timestamp}.{i}",
                # Let's say the bot message was sent 2 secs after
                "ticketTs": f"{timestamp + 2}.{i}",
                # User ID 1 should be the first user in the DB
                "openedBy": {"connect": {"id": 1}},
                # This prevents the "closing stale tickets" job getting angry at the fake tickets
                "status": TicketStatus.CLOSED,
            }
        )
    await send_heartbeat(f"Created {num_records} dummy ticket records.")
    logging.info(f"Successfully created {num_records} dummy ticket records.")


if __name__ == "__main__":
    if len(argv) < 2:
        print("Usage: python add_dummy_data.py <num_records>")
        exit(1)
    num_records = int(argv[1])
    asyncio.run(create_dummy_records(num_records))
