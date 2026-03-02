"""
Script simple para agregar campos a debt_payments sin dependencias complejas
"""

import psycopg
import os

# Configuración de conexión
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "finance_db")

conn_string = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"

try:
    with psycopg.connect(conn_string) as conn:
        with conn.cursor() as cur:
            # Agregar payment_method
            cur.execute(
                """
                ALTER TABLE debt_payments 
                ADD COLUMN IF NOT EXISTS payment_method VARCHAR(50)
            """
            )
            print("✓ Campo payment_method agregado")

            # Agregar voucher_filename
            cur.execute(
                """
                ALTER TABLE debt_payments 
                ADD COLUMN IF NOT EXISTS voucher_filename VARCHAR(255)
            """
            )
            print("✓ Campo voucher_filename agregado")

            # Agregar voucher_path
            cur.execute(
                """
                ALTER TABLE debt_payments 
                ADD COLUMN IF NOT EXISTS voucher_path VARCHAR(512)
            """
            )
            print("✓ Campo voucher_path agregado")

            conn.commit()

    print("\n✅ Migración completada exitosamente")

except Exception as e:
    print(f"\n❌ Error en migración: {e}")
    print("\nPuedes ejecutar manualmente en PostgreSQL:")
    print(
        "ALTER TABLE debt_payments ADD COLUMN IF NOT EXISTS payment_method VARCHAR(50);"
    )
    print(
        "ALTER TABLE debt_payments ADD COLUMN IF NOT EXISTS voucher_filename VARCHAR(255);"
    )
    print(
        "ALTER TABLE debt_payments ADD COLUMN IF NOT EXISTS voucher_path VARCHAR(512);"
    )
