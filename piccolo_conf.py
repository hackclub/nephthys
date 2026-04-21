from os import environ

from piccolo.conf.apps import AppRegistry
from piccolo.engine.postgres import PostgresEngine

db_url = environ.get("DATABASE_URL")
if not db_url:
    raise ValueError("DATABASE_URL environment variable is not set")

DB = PostgresEngine(config={"dsn": db_url})

# A list of paths to piccolo apps
# e.g. ['blog.piccolo_app']
APP_REGISTRY = AppRegistry(apps=["nephthys.piccolo_app"])
