from nephthys.database.raw_migration import raw_migration

ID = "2026-06-03T11:53:25:327785"
VERSION = "1.33.0"
DESCRIPTION = "Add app_home_last_view column to User table"


async def forwards():
    return raw_migration(
        migration_id=ID,
        app_name="nephthys",
        description=DESCRIPTION,
        forwards="""
ALTER TABLE "User" ADD COLUMN "appHomeLastView" TEXT;
""",
        backwards="""
ALTER TABLE "User" DROP COLUMN IF EXISTS "appHomeLastView";
""",
    )
