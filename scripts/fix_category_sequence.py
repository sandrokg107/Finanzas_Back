from app.database.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

try:
    # Arreglar el sequence de categories
    db.execute(
        text("SELECT setval('categories_id_seq', (SELECT MAX(id) FROM categories))")
    )
    db.commit()
    print("✓ Sequence de categorías actualizado")
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
