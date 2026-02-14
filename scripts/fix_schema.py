from sqlalchemy import text
from app.database.database import SessionLocal

db = SessionLocal()

try:
    # Agregar columna category_id a la tabla incomes
    db.execute(
        text(
            """
        ALTER TABLE incomes 
        ADD COLUMN IF NOT EXISTS category_id INTEGER 
        REFERENCES categories(id)
    """
        )
    )
    db.commit()
    print("✓ Columna category_id agregada a la tabla incomes")

except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
