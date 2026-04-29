from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.table import Table


ID = "2026-04-18T14:12:56:828491"
VERSION = "1.33.0"
DESCRIPTION = "Initial database state (nearly matching the old Prisma schema)"


# Dummy table we use to execute raw SQL with:
class RawTable(Table):
    pass


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="nephthys", description=DESCRIPTION
    )

    async def run():
        # Create the enums, unless they exist in either their modern snake_case
        # or legacy PascalCase form.
        await RawTable.raw(
            """DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_type
        WHERE typname IN ('ticket_status', 'TicketStatus')
    ) THEN
        CREATE TYPE ticket_status AS ENUM ('OPEN', 'IN_PROGRESS', 'CLOSED');
    END IF;
END
$$;"""
        )
        await RawTable.raw(
            """DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_type
        WHERE typname IN ('user_type', 'UserType')
    ) THEN
        CREATE TYPE user_type AS ENUM ('AUTHOR', 'HELPER', 'OTHER');
    END IF;
END
$$;"""
        )
        # Tables!
        await RawTable.raw(
            """
CREATE TABLE IF NOT EXISTS "User" (
  "id" SERIAL PRIMARY KEY, 
  "slackId" TEXT NOT NULL, 
  "username" TEXT,
  "admin" BOOLEAN NOT NULL DEFAULT false, 
  "helper" BOOLEAN NOT NULL DEFAULT false, 
  "createdAt" TIMESTAMP NOT NULL DEFAULT current_timestamp
);
"""
        )
        await RawTable.raw(
            """
CREATE TABLE IF NOT EXISTS "QuestionTag" (
  "id" SERIAL PRIMARY KEY, 
  "label" TEXT UNIQUE NOT NULL, 
  "createdAt" TIMESTAMP NOT NULL DEFAULT current_timestamp
);
"""
        )
        await RawTable.raw(
            """
CREATE TABLE IF NOT EXISTS "Tag" (
  "id" SERIAL PRIMARY KEY, 
  "name" TEXT UNIQUE NOT NULL, 
  "createdAt" TIMESTAMP NOT NULL DEFAULT current_timestamp
);
"""
        )
        await RawTable.raw(
            """
CREATE TABLE IF NOT EXISTS "CategoryTag" (
  "id" SERIAL PRIMARY KEY, 
  "name" TEXT UNIQUE NOT NULL, 
  "createdById" INTEGER REFERENCES "User" (id) ON DELETE CASCADE ON UPDATE CASCADE DEFAULT null, 
  "createdAt" TIMESTAMP NOT NULL DEFAULT current_timestamp
);
"""
        )
        await RawTable.raw(
            """
CREATE TABLE IF NOT EXISTS "Ticket" (
  "id" SERIAL PRIMARY KEY, 
  "title" TEXT NOT NULL, 
  "description" TEXT NOT NULL, 
  "status" "ticket_status" NOT NULL DEFAULT 'OPEN', 
  "msgTs" TEXT UNIQUE NOT NULL, 
  "ticketTs" TEXT UNIQUE NOT NULL, 
  "lastMsgAt" TIMESTAMP NOT NULL DEFAULT current_timestamp, 
  "lastMsgBy" "user_type" NOT NULL DEFAULT 'AUTHOR', 
  "openedById" INTEGER REFERENCES "User" (id) ON DELETE RESTRICT ON UPDATE CASCADE, 
  "reopenedById" INTEGER REFERENCES "User" (id) ON DELETE 
  SET 
    NULL ON UPDATE CASCADE DEFAULT null, 
    "closedById" INTEGER REFERENCES "User" (id) ON DELETE 
  SET 
    NULL ON UPDATE CASCADE DEFAULT null, 
    "assignedToId" INTEGER REFERENCES "User" (id) ON DELETE 
  SET 
    NULL ON UPDATE CASCADE DEFAULT null, 
    "assignedAt" TIMESTAMP, 
    "closedAt" TIMESTAMP, 
    "reopenedAt" TIMESTAMP, 
    "questionTagId" INTEGER REFERENCES "QuestionTag" (id) ON DELETE 
  SET 
    NULL ON UPDATE CASCADE DEFAULT null, 
    "categoryTagId" INTEGER REFERENCES "CategoryTag" (id) ON DELETE 
  SET 
    NULL ON UPDATE CASCADE DEFAULT null, 
    "createdAt" TIMESTAMP NOT NULL DEFAULT current_timestamp
);
"""
        )
        await RawTable.raw(
            """
CREATE TABLE IF NOT EXISTS "BotMessage" (
  "id" SERIAL PRIMARY KEY, 
  "ts" TEXT NOT NULL, 
  "channelId" TEXT NOT NULL, 
  "ticketId" INTEGER NOT NULL REFERENCES "Ticket" (id) ON DELETE CASCADE ON UPDATE CASCADE
);
"""
        )
        await RawTable.raw(
            """
CREATE TABLE IF NOT EXISTS "tags_on_tickets" (
  "ticketId" INTEGER NOT NULL REFERENCES "Ticket" (id) ON DELETE CASCADE ON UPDATE CASCADE, 
  "tagId" INTEGER NOT NULL REFERENCES "Tag" (id) ON DELETE CASCADE ON UPDATE CASCADE, 
  "assignedAt" TIMESTAMP NOT NULL DEFAULT current_timestamp,
  PRIMARY KEY ("ticketId", "tagId")
);
"""
        )
        await RawTable.raw(
            """
CREATE TABLE IF NOT EXISTS "user_tag_subscriptions" (
    "userId" INTEGER NOT NULL REFERENCES "User" (id) ON DELETE CASCADE ON UPDATE CASCADE,
    "tagId" INTEGER NOT NULL REFERENCES "Tag" (id) ON DELETE CASCADE ON UPDATE CASCADE,
    "subscribedAt" TIMESTAMP NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY ("userId", "tagId")
);
"""
        )
        # Other bits!
        await RawTable.raw(
            """
CREATE UNIQUE INDEX IF NOT EXISTS "BotMessage_ts_channelId_key" ON "BotMessage"("ts", "channelId");
"""
        )

    manager.add_raw(run)

    return manager
