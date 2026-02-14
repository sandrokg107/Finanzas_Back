from sqlalchemy import text
from app.database.database import SessionLocal

db = SessionLocal()

try:
    # Crear tabla credit_cards
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS credit_cards (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name VARCHAR(100) NOT NULL,
                credit_limit NUMERIC(12, 2) NOT NULL,
                used_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
                closing_day INTEGER NOT NULL CHECK (closing_day >= 1 AND closing_day <= 31)
            )
            """
        )
    )

    # Agregar columna payment_method a expenses
    db.execute(
        text(
            """
            ALTER TABLE expenses 
            ADD COLUMN IF NOT EXISTS payment_method VARCHAR(20) DEFAULT 'cash',
            ADD COLUMN IF NOT EXISTS credit_card_id INTEGER REFERENCES credit_cards(id) ON DELETE SET NULL
            """
        )
    )

    db.commit()
    print("✓ Tabla 'credit_cards' creada exitosamente")
    print("✓ Columnas 'payment_method' y 'credit_card_id' agregadas a 'expenses'")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
    db.rollback()
finally:
    db.close()
