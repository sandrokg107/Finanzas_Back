from sqlalchemy import text
from app.database.database import SessionLocal

db = SessionLocal()

try:
    # Actualizar tabla debts para el nuevo esquema
    print("Actualizando esquema de tabla debts...")

    # Agregar columna user_id
    db.execute(
        text(
            """
        ALTER TABLE debts 
        ADD COLUMN IF NOT EXISTS user_id INTEGER 
        REFERENCES users(id)
    """
        )
    )

    # Renombrar columna amount a total_amount si existe
    db.execute(
        text(
            """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='debts' AND column_name='amount'
            ) THEN
                ALTER TABLE debts RENAME COLUMN amount TO total_amount;
            END IF;
        END $$;
    """
        )
    )

    # Agregar columna paid_amount
    db.execute(
        text(
            """
        ALTER TABLE debts 
        ADD COLUMN IF NOT EXISTS paid_amount NUMERIC(12, 2) DEFAULT 0
    """
        )
    )

    # Eliminar columna is_paid si existe
    db.execute(
        text(
            """
        ALTER TABLE debts 
        DROP COLUMN IF EXISTS is_paid
    """
        )
    )

    # Agregar columna description
    db.execute(
        text(
            """
        ALTER TABLE debts 
        ADD COLUMN IF NOT EXISTS description TEXT
    """
        )
    )

    # Actualizar user_id para deudas existentes sin usuario (asignar a user 1)
    db.execute(
        text(
            """
        UPDATE debts 
        SET user_id = 1 
        WHERE user_id IS NULL
    """
        )
    )

    db.commit()
    print("✓ Esquema de tabla debts actualizado correctamente")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
    db.rollback()
finally:
    db.close()
