"""
Script para agregar el campo was_late a debt_payments
Permite registrar si un pago se realizó después de la fecha de vencimiento
"""

import sys
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text

from app.database.database import engine


def add_was_late_field():
    """Agrega el campo was_late a la tabla debt_payments"""
    with engine.connect() as conn:
        # Verificar si la columna ya existe
        result = conn.execute(
            text(
                """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'debt_payments' 
            AND column_name = 'was_late'
        """
            )
        )
        existing = result.fetchone()

        if not existing:
            print("Agregando columna 'was_late' a debt_payments...")
            conn.execute(
                text(
                    """
                ALTER TABLE debt_payments 
                ADD COLUMN was_late BOOLEAN NOT NULL DEFAULT FALSE
            """
                )
            )
            print("✓ Columna 'was_late' agregada")

            # Actualizar registros existentes: marcar como tarde si paid_date > due_date
            print("Actualizando registros existentes...")
            conn.execute(
                text(
                    """
                UPDATE debt_payments 
                SET was_late = TRUE 
                WHERE is_paid = TRUE 
                AND paid_date IS NOT NULL 
                AND paid_date > due_date
            """
                )
            )
            print("✓ Registros históricos actualizados")
        else:
            print("✓ Columna 'was_late' ya existe")

        conn.commit()
        print("\n✅ Migración completada exitosamente!")


if __name__ == "__main__":
    try:
        print("Iniciando migración de campo 'was_late' para pagos...\n")
        add_was_late_field()
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        sys.exit(1)
