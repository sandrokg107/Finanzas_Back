from sqlalchemy import inspect
from app.database.database import engine

inspector = inspect(engine)

print("=== Columnas en tabla 'incomes' ===")
for col in inspector.get_columns("incomes"):
    print(f" - {col['name']}: {col['type']}")

print("\n=== Columnas en tabla 'expenses' ===")
for col in inspector.get_columns("expenses"):
    print(f" - {col['name']}: {col['type']}")
