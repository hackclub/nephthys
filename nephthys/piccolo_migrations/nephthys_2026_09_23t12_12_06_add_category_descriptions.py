from nephthys.database.raw_migration import raw_migration

ID = "2026-09-23T12:12:06:165510"
VERSION = "1.34.0"
DESCRIPTION = "Add descriptions to category tags"


async def forwards():
    return raw_migration(
        migration_id=ID,
        app_name="nephthys",
        description=DESCRIPTION,
        forwards="""
ALTER TABLE "CategoryTag" ADD COLUMN description TEXT;
""",
        backwards="""
ALTER TABLE "CategoryTag" DROP COLUMN description;
""",
    )
