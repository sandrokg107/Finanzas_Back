# Backend - Personal Finance Manager

## Requisitos

- Python 3.11.9
- PostgreSQL 14+
- Git

## Versiones principales

- FastAPI 0.110.0
- SQLAlchemy 2.0.27
- Alembic 1.13.1
- Pydantic 2.6.1

## Instalacion rapida

1. Crear y activar entorno virtual

```powershell
python -m venv venv
venv\Scripts\activate
```

2. Instalar dependencias

```powershell
pip install -r requirements.txt
```

3. Crear .env a partir del ejemplo

```powershell
copy .env.example .env
```

4. Ejecutar el servidor

```powershell
uvicorn app.main:app --reload
```

## Migraciones (Alembic)

Inicializar base (si aplica)

```powershell
alembic revision --autogenerate -m "init"
alembic upgrade head
```

## Herramientas recomendadas

- Postman o Insomnia para probar endpoints
- DBeaver o pgAdmin para administrar PostgreSQL

## Notas

- No subas el archivo .env a git.
- Si usas Docker, revisa el Dockerfile.

## Deploy en Render (importante)

- Este proyecto fija Python en `3.11.9` con el archivo `.python-version`.
- Si Render usa `3.14+`, puede fallar la instalación de `pydantic-core`.
- Build command recomendado: `pip install -r requirements.txt`
- Start command recomendado: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- No usar `--reload` en producción.
- Si ya tienes un servicio creado, actualiza el Start Command en Render Dashboard (no cambia solo con git push).
- También puedes crear/sincronizar el servicio con `render.yaml` para versionar esta configuración.
