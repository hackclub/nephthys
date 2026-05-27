from nephthys.database.raw_migration import raw_migration

ID = "2026-05-26T16:43:09:804165"
VERSION = "1.33.0"
DESCRIPTION = ""


async def forwards():
    return raw_migration(
        migration_id=ID,
        app_name="nephthys",
        description=DESCRIPTION,
        forwards="""
CREATE TYPE feedback_rating AS ENUM ('GREAT', 'OKAY', 'NOT_GOOD');
CREATE TABLE "Feedback" (
  "id" SERIAL PRIMARY KEY UNIQUE NOT NULL, 
  "ticketId" INTEGER REFERENCES "Ticket" (id) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL, 
  "createdById" INTEGER REFERENCES "User" (id) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL, 
  "rating" feedback_rating NOT NULL, 
  "text" VARCHAR(32000),
  "createdAt" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
""",
        backwards="""
DROP TABLE IF EXISTS "Feedback";
DROP TYPE IF EXISTS feedback_rating;
""",
    )
