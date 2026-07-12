from nephthys.database.raw_migration import raw_migration

ID = "2026-05-07T11:04:02:747643"
VERSION = "1.33.0"
DESCRIPTION = "Add a UNIQUE INDEX to User.slackId"


async def forwards():
    # Duplicate Slack IDs are invalid
    # Also, we often look up based on Slack ID, so indexes are good here
    return raw_migration(
        migration_id=ID,
        app_name="nephthys",
        description=DESCRIPTION,
        forwards="""CREATE UNIQUE INDEX IF NOT EXISTS "User_slackId_key" ON "User" ("slackId");""",
        backwards="""DROP INDEX IF EXISTS "User_slackId_key";""",
    )
