"""Script para verificar usuarios en la base de datos."""

from app.database.database import SessionLocal
from app.models.user import User


def list_users():
    """Lista todos los usuarios en la base de datos."""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        if not users:
            print("No hay usuarios en la base de datos.")
            return

        print(f"Total de usuarios: {len(users)}\n")
        for user in users:
            print(f"ID: {user.id}")
            print(f"Email: {user.email}")
            print(f"Creado: {user.created_at}")
            print(f"Hash password (primeros 20 chars): {user.hashed_password[:20]}...")
            print("-" * 50)
    except Exception as e:
        print(f"Error al consultar usuarios: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    list_users()
