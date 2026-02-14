from sqlalchemy import text
from app.database.database import SessionLocal

db = SessionLocal()

try:
    # Crear tabla debt_payments
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS debt_payments (
                id SERIAL PRIMARY KEY,
                debt_id INTEGER NOT NULL REFERENCES debts(id) ON DELETE CASCADE,
                due_date DATE NOT NULL,
                amount NUMERIC(12, 2) NOT NULL,
                is_paid BOOLEAN NOT NULL DEFAULT FALSE,
                paid_date DATE
            )
            """
        )
    )

    # Agregar columna monthly_payment a debts
    db.execute(
        text(
            """
            ALTER TABLE debts 
            ADD COLUMN IF NOT EXISTS monthly_payment NUMERIC(12, 2)
            """
        )
    )

    db.commit()
    print("✓ Tabla 'debt_payments' creada exitosamente")
    print("✓ Columna 'monthly_payment' agregada a 'debts'")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
    db.rollback()
finally:
    db.close()
