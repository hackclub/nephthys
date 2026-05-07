# Dummy table we use to execute raw SQL with
from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.table import Table


class RawTable(Table):
    pass


def raw_migration(
    migration_id: str,
    app_name: str,
    description: str,
    forwards: str,
    backwards: str | None = None,
):
    manager = MigrationManager(
        migration_id=migration_id, app_name=app_name, description=description
    )

    async def run():
        await RawTable.raw(forwards)

    manager.add_raw(run)

    if backwards:

        async def run_backwards():
            await RawTable.raw(backwards)

        manager.add_raw_backwards(run_backwards)

    return manager
