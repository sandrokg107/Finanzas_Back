from app.database.database import SessionLocal
from app.models.category import Category

db = SessionLocal()

try:
    # Categorías adicionales
    new_categories = [
        "Vivienda",
        "Servicios",
        "Salud",
        "Educación",
        "Ropa",
        "Ahorro",
        "Inversión",
        "Deudas",
        "Otros",
    ]

    for name in new_categories:
        # Verificar si ya existe
        existing = db.query(Category).filter(Category.name == name).first()

        if not existing:
            category = Category(name=name)
            db.add(category)
            print(f"✓ Categoría '{name}' agregada")
        else:
            print(f"- Categoría '{name}' ya existe")

    db.commit()
    print(f"\n✓ Proceso completado")

    # Mostrar todas las categorías
    print("\nCategorías disponibles:")
    categories = db.query(Category).order_by(Category.id).all()
    for cat in categories:
        print(f"  {cat.id}: {cat.name}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
    db.rollback()
finally:
    db.close()
