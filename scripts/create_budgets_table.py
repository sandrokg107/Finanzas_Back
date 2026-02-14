from sqlalchemy import text
from app.database.database import SessionLocal

db = SessionLocal()

try:
    # Crear tabla budgets
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS budgets (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
                amount NUMERIC(12, 2) NOT NULL,
                month INTEGER NOT NULL CHECK (month >= 1 AND month <= 12),
                year INTEGER NOT NULL CHECK (year >= 2000 AND year <= 2100),
                UNIQUE(user_id, category_id, month, year)
            )
            """
        )
    )

    db.commit()
    print("✓ Tabla 'budgets' creada exitosamente")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
    db.rollback()
finally:
    db.close()
