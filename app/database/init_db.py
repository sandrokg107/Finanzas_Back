import psycopg
from psycopg import sql

from app.core.config import settings


def create_database_if_not_exists() -> None:
    conn = psycopg.connect(
        f"dbname=postgres user={settings.DB_USER} "
        f"password={settings.DB_PASSWORD} host={settings.DB_HOST} "
        f"port={settings.DB_PORT}"
    )
    conn.autocommit = True
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s",
        (settings.DB_NAME,),
    )
    exists = cursor.fetchone()

    if not exists:
        cursor.execute(
            sql.SQL("CREATE DATABASE {}").format(sql.Identifier(settings.DB_NAME))
        )

    cursor.close()
    conn.close()
