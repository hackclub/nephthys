from nephthys.database.raw_migration import raw_migration

ID = "2026-09-23T21:06:48:905346"
VERSION = "1.34.0"
DESCRIPTION = "Migrate old placeholder ticket titles to NULL"


async def forwards():
    return raw_migration(
        migration_id=ID,
        app_name="nephthys",
        description=DESCRIPTION,
        forwards="""
UPDATE "Ticket"
SET "title" = NULL
WHERE "title" = 'No title provided by AI.'
 OR "title" = 'No title available from AI.';
""",
    )
