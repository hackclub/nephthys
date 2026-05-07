from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.table import Table


ID = "2026-05-07T10:40:49:822926"
VERSION = "1.33.0"
DESCRIPTION = "Removes the UNIQUE INDEX from User.username"


class RawTable(Table):
    pass


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="nephthys", description=DESCRIPTION
    )

    async def run():
        # This only affects legacy (Prisma) databases, which had a
        # UNIQUE constraint on the username field.
        # This could fail if two users "swap" usernames, so let's
        # just remove it.
        await RawTable.raw('''DROP INDEX IF EXISTS "User_username_key"''')

    manager.add_raw(run)

    return manager
