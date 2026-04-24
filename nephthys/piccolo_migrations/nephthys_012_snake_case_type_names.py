from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.table import Table

ID = "2026-04-24T16:36:11:002312"
VERSION = "1.33.0"
DESCRIPTION = "Rename legacy TicketStatus and UserType enum types to snake_case"


class RawTable(Table):
    pass


async def forwards():
    manager = MigrationManager(migration_id=ID, app_name="", description=DESCRIPTION)

    def run():
        # For fresh databases created after the Piccolo migration, this won't do anything.
        # For databases that had the Prisma data structure, this renames the types to match
        # the new snake_case naming convention.
        RawTable.raw("""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'TicketStatus') THEN
                    ALTER TYPE "TicketStatus" RENAME TO ticket_status;
                END IF;

                IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'UserType') THEN
                    ALTER TYPE "UserType" RENAME TO user_type;
                END IF;
            END$$;
        """)

    manager.add_raw(run)

    return manager
