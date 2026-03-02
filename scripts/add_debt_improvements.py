"""
Script para agregar mejoras al sistema de deudas:
- total_installments: Número total de cuotas
- payment_day: Día del mes de pago (1-31)
- reminder_days: Días de anticipación para recordatorios (default: 3)
"""

import sys
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text

from app.database.database import engine


def add_debt_improvements():
    """Agrega los campos nuevos a la tabla debts"""
    with engine.connect() as conn:
        # Verificar si las columnas ya existen
        result = conn.execute(
            text(
                """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'debts' 
            AND column_name IN ('total_installments', 'payment_day', 'reminder_days')
        """
            )
        )
        existing_columns = {row[0] for row in result}

        # Agregar total_installments si no existe
        if "total_installments" not in existing_columns:
            print("Agregando columna 'total_installments'...")
            conn.execute(
                text(
                    """
                ALTER TABLE debts 
                ADD COLUMN total_installments INTEGER NULL
            """
                )
            )
            print("✓ Columna 'total_installments' agregada")
        else:
            print("✓ Columna 'total_installments' ya existe")

        # Agregar payment_day si no existe
        if "payment_day" not in existing_columns:
            print("Agregando columna 'payment_day'...")
            conn.execute(
                text(
                    """
                ALTER TABLE debts 
                ADD COLUMN payment_day INTEGER NULL
            """
                )
            )
            print("✓ Columna 'payment_day' agregada")
        else:
            print("✓ Columna 'payment_day' ya existe")

        # Agregar reminder_days si no existe
        if "reminder_days" not in existing_columns:
            print("Agregando columna 'reminder_days'...")
            conn.execute(
                text(
                    """
                ALTER TABLE debts 
                ADD COLUMN reminder_days INTEGER DEFAULT 3
            """
                )
            )
            print("✓ Columna 'reminder_days' agregada")

            # Actualizar registros existentes para que tengan el valor por defecto
            conn.execute(
                text(
                    """
                UPDATE debts 
                SET reminder_days = 3 
                WHERE reminder_days IS NULL
            """
                )
            )
            print("✓ Valores por defecto aplicados a registros existentes")
        else:
            print("✓ Columna 'reminder_days' ya existe")

        conn.commit()
        print("\n✅ Migración completada exitosamente!")


if __name__ == "__main__":
    try:
        print("Iniciando migración de mejoras para deudas...\n")
        add_debt_improvements()
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        sys.exit(1)
