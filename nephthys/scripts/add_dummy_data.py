import asyncio
import logging
from datetime import datetime
from datetime import timedelta
from random import randint
from sys import argv

from nephthys.database.tables import Ticket
from nephthys.database.tables import TicketStatus
from nephthys.utils.logging import send_heartbeat


async def create_dummy_records(num_records: int):
    # We generate random timestamps from up to 2 weeks ago
    timestamp_a = datetime.now() - timedelta(weeks=2)
    timestamp_b = datetime.now()
    timestamp_range = (int(timestamp_a.timestamp()), int(timestamp_b.timestamp()))
    for i in range(num_records):
        timestamp = randint(*timestamp_range)
        ticket = Ticket(
            title=f"Test ticket {i}",
            description=f"Test ticket number {i}",
            msg_ts=f"{timestamp}.{i}",
            ticket_ts=f"{timestamp + 2}.{i}",
            opened_by=1,
            status=TicketStatus.CLOSED,
            closed_by=1,
            assigned_to=1,
            assigned_at=datetime.fromtimestamp(timestamp + 10),
            closed_at=datetime.fromtimestamp(timestamp + 110),
        )
        await ticket.save()
    await send_heartbeat(f"Created {num_records} dummy ticket records.")
    logging.info(f"Successfully created {num_records} dummy ticket records.")


if __name__ == "__main__":
    if len(argv) < 2:
        print("Usage: python add_dummy_data.py <num_records>")
        exit(1)
    num_records = int(argv[1])
    asyncio.run(create_dummy_records(num_records))
