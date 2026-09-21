from nephthys.database.raw_migration import raw_migration

ID = "2026-09-21T22:35:27:487945"
VERSION = "1.34.0"
DESCRIPTION = "Add api_key table"


async def forwards():
    return raw_migration(
        migration_id=ID,
        app_name="nephthys",
        description=DESCRIPTION,
        forwards="""
CREATE TABLE api_key (
    id SERIAL PRIMARY KEY,
    label TEXT NOT NULL,
    user_id INT NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
    api_key_hash TEXT NOT NULL UNIQUE,
    api_key_censored TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""",
        backwards="""
DROP TABLE IF EXISTS api_key;
""",
    )
