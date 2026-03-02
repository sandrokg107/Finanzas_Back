"""
Script para agregar campos de método de pago y comprobante a debt_payments
"""

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()


def add_payment_fields():
    # Construir la URL de conexión desde variables de entorno
    db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    engine = create_engine(db_url)

    with engine.connect() as conn:
        # Agregar payment_method
        try:
            conn.execute(
                text(
                    """
                ALTER TABLE debt_payments 
                ADD COLUMN IF NOT EXISTS payment_method VARCHAR(50)
            """
                )
            )
            print("✓ Campo payment_method agregado")
        except Exception as e:
            print(f"payment_method: {e}")

        # Agregar voucher_filename
        try:
            conn.execute(
                text(
                    """
                ALTER TABLE debt_payments 
                ADD COLUMN IF NOT EXISTS voucher_filename VARCHAR(255)
            """
                )
            )
            print("✓ Campo voucher_filename agregado")
        except Exception as e:
            print(f"voucher_filename: {e}")

        # Agregar voucher_path
        try:
            conn.execute(
                text(
                    """
                ALTER TABLE debt_payments 
                ADD COLUMN IF NOT EXISTS voucher_path VARCHAR(512)
            """
                )
            )
            print("✓ Campo voucher_path agregado")
        except Exception as e:
            print(f"voucher_path: {e}")

        conn.commit()

    print("\n✅ Migración completada")


if __name__ == "__main__":
    add_payment_fields()
