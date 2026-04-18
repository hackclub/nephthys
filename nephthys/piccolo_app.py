import os

from piccolo.conf.apps import AppConfig

from nephthys.database.tables import ALL_TABLES

CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


APP_CONFIG = AppConfig(
    app_name="nephthys",
    migrations_folder_path=os.path.join(CURRENT_DIRECTORY, "piccolo_migrations"),
    table_classes=ALL_TABLES,
    migration_dependencies=[],
    commands=[],
)
