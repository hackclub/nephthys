from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.table import Table


ID = "2026-04-21T09:40:37.881242"
VERSION = "1.33.0"
DESCRIPTION = "Convert legacy TIMESTAMP columns to TIMESTAMPTZ"


# Dummy table we use to execute raw SQL with
class RawTable(Table):
    pass


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="nephthys", description=DESCRIPTION
    )

    async def run():
        # Important note: We assume that timestamps were previously stored in UTC
        # This is true for all the official Nephthys deployments (on Coolify)
        # but should be double-checked for self-hosted Nephthys deployments!
        await RawTable.raw(
            """
ALTER TABLE "User"
ALTER COLUMN "createdAt" TYPE TIMESTAMPTZ USING "createdAt" AT TIME ZONE 'UTC';
"""
        )

        await RawTable.raw(
            """
ALTER TABLE "QuestionTag"
ALTER COLUMN "createdAt" TYPE TIMESTAMPTZ USING "createdAt" AT TIME ZONE 'UTC';
"""
        )

        await RawTable.raw(
            """
ALTER TABLE "Tag"
ALTER COLUMN "createdAt" TYPE TIMESTAMPTZ USING "createdAt" AT TIME ZONE 'UTC';
"""
        )

        await RawTable.raw(
            """
ALTER TABLE "CategoryTag"
ALTER COLUMN "createdAt" TYPE TIMESTAMPTZ USING "createdAt" AT TIME ZONE 'UTC';
"""
        )

        await RawTable.raw(
            """
ALTER TABLE "Ticket"
ALTER COLUMN "lastMsgAt" TYPE TIMESTAMPTZ USING "lastMsgAt" AT TIME ZONE 'UTC',
ALTER COLUMN "assignedAt" TYPE TIMESTAMPTZ USING "assignedAt" AT TIME ZONE 'UTC',
ALTER COLUMN "closedAt" TYPE TIMESTAMPTZ USING "closedAt" AT TIME ZONE 'UTC',
ALTER COLUMN "reopenedAt" TYPE TIMESTAMPTZ USING "reopenedAt" AT TIME ZONE 'UTC',
ALTER COLUMN "createdAt" TYPE TIMESTAMPTZ USING "createdAt" AT TIME ZONE 'UTC';
"""
        )

        await RawTable.raw(
            """
ALTER TABLE "tags_on_tickets"
ALTER COLUMN "assignedAt" TYPE TIMESTAMPTZ USING "assignedAt" AT TIME ZONE 'UTC';
"""
        )

        await RawTable.raw(
            """
ALTER TABLE "user_tag_subscriptions"
ALTER COLUMN "subscribedAt" TYPE TIMESTAMPTZ USING "subscribedAt" AT TIME ZONE 'UTC';
"""
        )

    manager.add_raw(run)

    return manager
