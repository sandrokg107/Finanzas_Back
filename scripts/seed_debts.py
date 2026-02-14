from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import text
from app.database.database import SessionLocal

db = SessionLocal()

try:
    user_id = 1
    today = date.today()

    # Crear deudas de prueba
    debts_data: list[dict[str, Any]] = [
        {
            "user_id": user_id,
            "creditor": "Banco Nacional",
            "total_amount": Decimal("5000.00"),
            "paid_amount": Decimal("1500.00"),
            "due_date": today + timedelta(days=90),
            "description": "Préstamo personal",
        },
        {
            "user_id": user_id,
            "creditor": "Tarjeta de Crédito Visa",
            "total_amount": Decimal("2000.00"),
            "paid_amount": Decimal("500.00"),
            "due_date": today + timedelta(days=30),
            "description": "Saldo de tarjeta de crédito",
        },
        {
            "user_id": user_id,
            "creditor": "Préstamo Familiar",
            "total_amount": Decimal("1000.00"),
            "paid_amount": Decimal("0.00"),
            "due_date": today + timedelta(days=60),
            "description": "Préstamo de mi hermano",
        },
    ]

    for debt in debts_data:
        db.execute(
            text(
                """
                INSERT INTO debts (user_id, creditor, total_amount, paid_amount, due_date, description)
                VALUES (:user_id, :creditor, :total_amount, :paid_amount, :due_date, :description)
            """
            ),
            debt,
        )

    db.commit()
    print(f"✓ {len(debts_data)} deudas de prueba creadas")
    print("\nDeudas creadas:")
    for debt in debts_data:
        remaining = debt["total_amount"] - debt["paid_amount"]
        print(
            f"  - {debt['creditor']}: ${debt['total_amount']} (Pagado: ${debt['paid_amount']}, Resta: ${remaining})"
        )

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
    db.rollback()
finally:
    db.close()
