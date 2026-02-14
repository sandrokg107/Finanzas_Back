from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import text
from app.database.database import SessionLocal


def seed_database():
    db = SessionLocal()
    try:
        # Crear categorías
        cat_names = ["Salario", "Freelance", "Comida", "Transporte", "Entretenimiento"]
        category_map: dict[str, int] = {}

        for name in cat_names:
            result = db.execute(
                text("SELECT id FROM categories WHERE name = :name"), {"name": name}
            ).fetchone()

            if result:
                category_map[name] = result[0]
            else:
                result = db.execute(
                    text("INSERT INTO categories (name) VALUES (:name) RETURNING id"),
                    {"name": name},
                )
                row = result.fetchone()
                if row is None:
                    raise RuntimeError("No se pudo crear la categoria")
                category_map[name] = row[0]

        db.commit()
        print(f"✓ {len(category_map)} categorías disponibles")

        # Crear ingresos de prueba
        user_id = 1
        today = date.today()

        incomes_data = [
            (
                Decimal("3000.00"),
                "Salario mensual",
                today - timedelta(days=5),
                category_map["Salario"],
            ),
            (
                Decimal("500.00"),
                "Proyecto freelance",
                today - timedelta(days=3),
                category_map["Freelance"],
            ),
        ]

        for amount, desc, d, cat_id in incomes_data:
            db.execute(
                text(
                    "INSERT INTO incomes (amount, description, date, category_id, user_id) VALUES (:a, :d, :dt, :c, :u)"
                ),
                {"a": amount, "d": desc, "dt": d, "c": cat_id, "u": user_id},
            )

        db.commit()
        print(f"✓ {len(incomes_data)} ingresos creados")

        # Crear gastos de prueba
        expenses_data = [
            (
                Decimal("150.00"),
                "Supermercado",
                today - timedelta(days=4),
                category_map["Comida"],
            ),
            (
                Decimal("30.00"),
                "Taxi",
                today - timedelta(days=2),
                category_map["Transporte"],
            ),
            (
                Decimal("80.00"),
                "Cine y cena",
                today - timedelta(days=1),
                category_map["Entretenimiento"],
            ),
        ]

        for amount, desc, d, cat_id in expenses_data:
            db.execute(
                text(
                    "INSERT INTO expenses (amount, description, date, category_id, user_id) VALUES (:a, :d, :dt, :c, :u)"
                ),
                {"a": amount, "d": desc, "dt": d, "c": cat_id, "u": user_id},
            )

        db.commit()
        print(f"✓ {len(expenses_data)} gastos creados")

        print("\n✅ Datos de prueba creados exitosamente!")
        print(f"Usuario ID: {user_id}")
        print(f"Ingresos totales: $3,500.00")
        print(f"Gastos totales: $260.00")
        print(f"Balance: $3,240.00")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
