from nephthys.database.raw_migration import raw_migration

ID = "2026-09-23T23:33:47:020464"
VERSION = "1.34.0"
DESCRIPTION = "Add slugs to category tags"


async def forwards():
    return raw_migration(
        migration_id=ID,
        app_name="nephthys",
        description=DESCRIPTION,
        forwards="""
ALTER TABLE "CategoryTag" ADD COLUMN slug TEXT;

-- Backfill slugs for existing tags by snake_casing their name
UPDATE "CategoryTag"
SET slug = trim(both '_' from regexp_replace(lower("name"), '[^a-z0-9]+', '_', 'g'));

ALTER TABLE "CategoryTag" ALTER COLUMN slug SET NOT NULL;
ALTER TABLE "CategoryTag" ADD CONSTRAINT "CategoryTag_slug_key" UNIQUE (slug);
""",
        backwards="""
ALTER TABLE "CategoryTag" DROP CONSTRAINT IF EXISTS "CategoryTag_slug_key";
ALTER TABLE "CategoryTag" DROP COLUMN slug;
""",
    )
