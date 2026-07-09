import argparse
import asyncio
import logging
from datetime import datetime
from datetime import timedelta
from random import randint

from nephthys.database.enums import TicketStatus
from nephthys.database.tables import Ticket
from nephthys.database.tables import User
from nephthys.utils.logging import send_heartbeat


async def get_default_user() -> User:
    user = await User.objects().first()
    if not user:
        raise RuntimeError("No users found in database")
    return user


async def create_dummy_records(num_records: int, assigned_to: int | None = None):
    default_user = await get_default_user()
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
            opened_by=default_user,
            status=TicketStatus.CLOSED,
            closed_by=default_user,
            assigned_to=assigned_to or default_user,
            assigned_at=datetime.fromtimestamp(timestamp + 10),
            closed_at=datetime.fromtimestamp(timestamp + 110),
        )
        await ticket.save()
    await send_heartbeat(f"Created {num_records} dummy ticket records.")
    logging.info(f"Successfully created {num_records} dummy ticket records.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--count", type=int, required=True, help="number of tickets to create"
    )
    parser.add_argument(
        "--assigned-to", type=int, help="assign all tickets to this user id"
    )
    args = parser.parse_args()

    asyncio.run(create_dummy_records(args.count, args.assigned_to))
