from nephthys.database.raw_migration import raw_migration

ID = "2026-09-23T20:31:23:084733"
VERSION = "1.34.0"
DESCRIPTION = "Make ticket titles nullable"


async def forwards():
    return raw_migration(
        migration_id=ID,
        app_name="nephthys",
        description=DESCRIPTION,
        forwards="""
ALTER TABLE "Ticket" ALTER COLUMN "title" DROP NOT NULL;
""",
        backwards="""
ALTER TABLE "Ticket" ALTER COLUMN "title" SET NOT NULL;
""",
    )
