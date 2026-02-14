"""Script para crear un usuario directamente en la base de datos."""

import sys

from app.core.security import hash_password
from app.database.database import SessionLocal
from app.models.user import User


def create_user(email: str, password: str) -> None:
    """Crea un usuario en la base de datos."""
    db = SessionLocal()
    try:
        # Verificar si ya existe
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"Error: El usuario {email} ya existe.")
            return

        # Crear usuario
        user = User(
            email=email,
            hashed_password=hash_password(password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✓ Usuario creado exitosamente:")
        print(f"  Email: {email}")
        print(f"  ID: {user.id}")
    except Exception as e:
        db.rollback()
        print(f"Error al crear usuario: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python create_user.py <email> <password>")
        print("Ejemplo: python create_user.py admin@example.com password123")
        sys.exit(1)

    email = sys.argv[1]
    password = sys.argv[2]

    create_user(email, password)
