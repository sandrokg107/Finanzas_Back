"""Script para probar el login del usuario."""

import sys

import httpx

from app.core.security import verify_password
from app.database.database import SessionLocal
from app.models.user import User


def test_login_local(email: str, password: str):
    """Prueba el login localmente (sin API)."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"❌ Usuario no encontrado: {email}")
            return False

        if verify_password(password, user.hashed_password):
            print(f"✓ Login LOCAL exitoso para {email}")
            return True
        else:
            print(f"❌ Contraseña incorrecta para {email}")
            return False
    finally:
        db.close()


def test_login_api(email: str, password: str):
    """Prueba el login contra la API."""
    try:
        response = httpx.post(
            "http://127.0.0.1:8000/api/v1/auth/login",
            data={"username": email, "password": password},
            timeout=5.0,
        )
        if response.status_code == 200:
            print(f"✓ Login API exitoso para {email}")
            print(f"  Token: {response.json()['access_token'][:30]}...")
            return True
        else:
            print(f"❌ Login API falló: {response.status_code}")
            print(f"  Respuesta: {response.text}")
            return False
    except httpx.ConnectError:
        print(
            "❌ No se pudo conectar al servidor. Asegúrate de que el backend esté corriendo."
        )
        return False
    except Exception as e:
        print(f"❌ Error al probar login API: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) != 3:
        email = "admin@lumina.com"
        password = "admin123"
        print(f"Usando credenciales por defecto: {email}")
    else:
        email = sys.argv[1]
        password = sys.argv[2]

    print(f"\n🔍 Probando credenciales: {email}\n")
    print("=" * 60)

    print("\n1. Prueba LOCAL (verificación directa en DB):")
    local_ok = test_login_local(email, password)

    print("\n2. Prueba API (endpoint /auth/login):")
    api_ok = test_login_api(email, password)

    print("\n" + "=" * 60)
    if local_ok and api_ok:
        print("✓ TODAS las pruebas pasaron")
    elif local_ok and not api_ok:
        print("⚠ El usuario existe pero hay un problema con el API")
        print("  Verifica que el backend esté corriendo en http://127.0.0.1:8000")
    else:
        print("❌ Hay un problema con las credenciales")
