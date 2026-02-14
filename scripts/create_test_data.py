from datetime import date, timedelta
from decimal import Decimal

from app.database.database import SessionLocal
from app.models.income import Income
from app.models.expense import Expense
from app.models.category import Category


def create_test_data():
    db = SessionLocal()
    try:
        # Crear categorías si no existen
        cat_names = ["Salario", "Freelance", "Comida", "Transporte", "Entretenimiento"]
        category_map: dict[str, int] = {}

        for name in cat_names:
            existing = db.query(Category).filter(Category.name == name).first()
            if existing:
                category_map[name] = existing.id
            else:
                cat = Category(name=name)
                db.add(cat)
                db.flush()
                category_map[name] = cat.id

        db.commit()
        print(f"✓ {len(category_map)} categorías disponibles")

        # Crear ingresos de prueba
        user_id = 1  # admin@lumina.com
        today = date.today()

        incomes = [
            Income(
                amount=Decimal("3000.00"),
                description="Salario mensual",
                date=today - timedelta(days=5),
                category_id=category_map["Salario"],
                user_id=user_id,
            ),
            Income(
                amount=Decimal("500.00"),
                description="Proyecto freelance",
                date=today - timedelta(days=3),
                category_id=category_map["Freelance"],
                user_id=user_id,
            ),
        ]

        for income in incomes:
            db.add(income)

        db.flush()
        print(f"✓ {len(incomes)} ingresos creados")

        expenses = [
            Expense(
                amount=Decimal("150.00"),
                description="Supermercado",
                date=today - timedelta(days=4),
                category_id=category_map["Comida"],
                user_id=user_id,
            ),
            Expense(
                amount=Decimal("30.00"),
                description="Taxi",
                date=today - timedelta(days=2),
                category_id=category_map["Transporte"],
                user_id=user_id,
            ),
            Expense(
                amount=Decimal("80.00"),
                description="Cine y cena",
                date=today - timedelta(days=1),
                category_id=category_map["Entretenimiento"],
                user_id=user_id,
            ),
        ]

        for expense in expenses:
            db.add(expense)

        print(f"✓ {len(expenses)} gastos creados")

        db.commit()
        print("\n✅ Datos de prueba creados exitosamente!")
        print(f"Usuario ID: {user_id}")
        print(f"Ingresos totales: $3,500.00")
        print(f"Gastos totales: $260.00")
        print(f"Balance: $3,240.00")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_test_data()
