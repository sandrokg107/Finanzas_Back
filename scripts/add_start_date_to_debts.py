"""
Migración: Agregar columna start_date a la tabla debts
"""

from typing import Any, Protocol, cast

import psycopg  # type: ignore[import-not-found]

psycopg_any: Any = psycopg


class CursorLike(Protocol):
    def execute(self, query: str) -> None: ...
    def close(self) -> None: ...


class ConnectionLike(Protocol):
    def cursor(self) -> CursorLike: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
    def close(self) -> None: ...


from app.core.config import settings


def run_migration():
    """Agrega la columna start_date a la tabla debts"""

    conn_string = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    conn: ConnectionLike = cast(ConnectionLike, psycopg_any.connect(conn_string))
    cursor: CursorLike = conn.cursor()

    try:
        # Agregar columna start_date
        cursor.execute(
            """
            ALTER TABLE debts
            ADD COLUMN IF NOT EXISTS start_date DATE;
        """
        )

        conn.commit()
        print("✓ Columna 'start_date' agregada a la tabla 'debts' exitosamente")

    except Exception as e:
        conn.rollback()
        print(f"✗ Error al agregar columna 'start_date': {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    run_migration()
