from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.table import Table


ID = "2026-04-18T14:12:56:828491"
VERSION = "1.33.0"
DESCRIPTION = "Initial database state before we adopted Piccolo"


# Dummy table we use to execute raw SQL with:
class RawTable(Table):
    pass


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="nephthys", description=DESCRIPTION
    )

    async def run():
        await RawTable.raw(
            """
CREATE TYPE ticket_status AS ENUM ('OPEN', 'IN_PROGRESS', 'CLOSED');
"""
        )
        await RawTable.raw(
            """
CREATE TYPE user_type AS ENUM ('AUTHOR', 'HELPER', 'OTHER');
"""
        )
        await RawTable.raw(
            """
CREATE TABLE "User" (
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
CREATE TABLE "QuestionTag" (
  "id" SERIAL PRIMARY KEY, 
  "label" TEXT UNIQUE NOT NULL, 
  "createdAt" TIMESTAMP NOT NULL DEFAULT current_timestamp
);
"""
        )
        await RawTable.raw(
            """
CREATE TABLE "Tag" (
  "id" SERIAL PRIMARY KEY, 
  "name" TEXT UNIQUE NOT NULL, 
  "createdAt" TIMESTAMP NOT NULL DEFAULT current_timestamp
);
"""
        )
        await RawTable.raw(
            """
CREATE TABLE "CategoryTag" (
  "id" SERIAL PRIMARY KEY, 
  "name" TEXT UNIQUE NOT NULL, 
  "createdById" INTEGER REFERENCES "User" (id) ON DELETE CASCADE ON UPDATE CASCADE DEFAULT null, 
  "createdAt" TIMESTAMP NOT NULL DEFAULT current_timestamp
);
"""
        )
        await RawTable.raw(
            """
CREATE TABLE "Ticket" (
  "id" SERIAL PRIMARY KEY, 
  "title" TEXT NOT NULL, 
  "description" TEXT NOT NULL, 
  "status" "ticket_status" NOT NULL DEFAULT 'OPEN', 
  "msgTs" TEXT UNIQUE NOT NULL, 
  "ticketTs" TEXT UNIQUE NOT NULL, 
  "lastMsgAt" TIMESTAMP NOT NULL DEFAULT current_timestamp, 
  "lastMsgBy" "user_type" NOT NULL DEFAULT 'AUTHOR', 
  "openedById" INTEGER REFERENCES "User" (id) ON DELETE RESTRICT ON UPDATE CASCADE DEFAULT null, 
  "reopenedById" INTEGER REFERENCES "User" (id) ON DELETE 
  SET 
    NULL ON UPDATE CASCADE DEFAULT null, 
    "closedById" INTEGER REFERENCES "User" (id) ON DELETE 
  SET 
    NULL ON UPDATE CASCADE DEFAULT null, 
    "assignedToId" INTEGER REFERENCES "User" (id) ON DELETE 
  SET 
    NULL ON UPDATE CASCADE DEFAULT null, 
    "assignedAt" TIMESTAMP DEFAULT current_timestamp, 
    "closedAt" TIMESTAMP DEFAULT current_timestamp, 
    "reopenedAt" TIMESTAMP DEFAULT current_timestamp, 
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
CREATE TABLE "BotMessage" (
  "id" SERIAL PRIMARY KEY, 
  "ts" TEXT NOT NULL, 
  "channelId" TEXT NOT NULL, 
  "ticketId" INTEGER NOT NULL REFERENCES "Ticket" (id) ON DELETE CASCADE ON UPDATE CASCADE
);
"""
        )
        await RawTable.raw(
            """
CREATE TABLE "tags_on_tickets" (
  "ticketId" INTEGER NOT NULL REFERENCES "Ticket" (id) ON DELETE CASCADE ON UPDATE CASCADE, 
  "tagId" INTEGER NOT NULL REFERENCES "Tag" (id) ON DELETE CASCADE ON UPDATE CASCADE, 
  "assignedAt" TIMESTAMP NOT NULL DEFAULT current_timestamp,
  PRIMARY KEY ("ticketId", "tagId")
);
"""
        )
        await RawTable.raw(
            """
CREATE TABLE "user_tag_subscriptions" (
    "userId" INTEGER NOT NULL REFERENCES "User" (id) ON DELETE CASCADE ON UPDATE CASCADE,
    "tagId" INTEGER NOT NULL REFERENCES "Tag" (id) ON DELETE CASCADE ON UPDATE CASCADE,
    "subscribedAt" TIMESTAMP NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY ("userId", "tagId")
);
"""
        )
        await RawTable.raw(
            """
CREATE UNIQUE INDEX "BotMessage_ts_channelId_key" ON "BotMessage"("ts", "channelId");
"""
        )

    manager.add_raw(run)

    return manager
