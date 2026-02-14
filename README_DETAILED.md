# 🔧 Backend - Lumina Finance API

> API REST en FastAPI para gestionar finanzas personales, deudas, presupuestos y tarjetas de crédito.

![Python](https://img.shields.io/badge/python-3.11-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/fastapi-0.110-green?style=flat-square)
![PostgreSQL](https://img.shields.io/badge/postgresql-14+-blue?style=flat-square)
![Status](https://img.shields.io/badge/status-activo-green?style=flat-square)

## 📋 Tabla de Contenidos

- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Modelos de Datos](#modelos-de-datos)
- [Endpoints API](#endpoints-api)
- [Autenticación](#autenticación)
- [Migraciones](#migraciones)
- [Desarrollo](#desarrollo)
- [Troubleshooting](#troubleshooting)

## 📦 Requisitos

- **Python 3.11.9** o superior
- **PostgreSQL 14+** (local o remoto)
- **pip** (gestor de paquetes Python)
- **Git** (opcional, para control de versiones)

### Stack Tecnológico

| Componente       | Versión | Descripción            |
| ---------------- | ------- | ---------------------- |
| FastAPI          | 0.110.0 | Framework web moderno  |
| SQLAlchemy       | 2.0.27  | ORM para SQL           |
| Pydantic         | 2.6.1+  | Validación de datos    |
| psycopg          | 3.1.18  | Driver PostgreSQL      |
| python-jose      | 3.3.0   | JWT para autenticación |
| bcrypt           | 4.1.2   | Hash de contraseñas    |
| Alembic          | 1.13.1  | Migraciones de BD      |
| python-multipart | 0.0.6   | Manejo de formularios  |
| email-validator  | 2.1.0   | Validación de emails   |

## 🚀 Instalación

### 1. Clonar Repositorio

```bash
git clone https://github.com/usuario/lumina-finance.git
cd lumina-finance/backend
```

### 2. Crear Entorno Virtual

**Windows (PowerShell):**

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

**Linux/Mac:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Crear archivo `.env` en la carpeta backend:

```bash
# Base de Datos
DB_USER=postgres
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=5432
DB_NAME=lumina_finance

# Seguridad
SECRET_KEY=tu_clave_secreta_muy_larga_y_segura_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Desarrollo
DEBUG=True
```

### 5. Inicializar Base de Datos

```bash
# Ejecutar migraciones (si existen)
python migrate.py

# O crear tablas manualmente
python -c "from app.database.database import Base, engine; Base.metadata.create_all(bind=engine)"

# Insertar datos iniciales (opcional)
python -c "from app.database.init_db import init_db; init_db()"
```

### 6. Ejecutar Servidor

```bash
# Desarrollo con auto-reload
python run.py

# O directamente con uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

El servidor estará disponible en: **http://localhost:8000**

## ⚙️ Configuración

### Variables de Entorno Principales

```env
# 🗄️ Base de Datos PostgreSQL
DB_USER=postgres              # Usuario BD
DB_PASSWORD=password123       # Contraseña BD
DB_HOST=localhost             # Host del servidor
DB_PORT=5432                  # Puerto (default: 5432)
DB_NAME=lumina_finance        # Nombre de la base de datos

# 🔐 Seguridad
SECRET_KEY=cambiar_esto_por_algo_muy_seguro  # Clave para JWT
ALGORITHM=HS256               # Algoritmo JWT
ACCESS_TOKEN_EXPIRE_MINUTES=30 # Expiración del token

# 🛠️ Desarrollo
DEBUG=True                    # Activar debug mode
LOG_LEVEL=INFO                # Nivel de logging
```

### Conexión a PostgreSQL

**Instalación en Windows:**

```bash
# Descargar desde https://www.postgresql.org/download/
# O con chocolatey:
choco install postgresql
```

**Crear Base de Datos:**

```bash
# Conectarse como admin
psql -U postgres

# En psql:
CREATE DATABASE lumina_finance;
\q
```

## 📁 Estructura del Proyecto

```
backend/
├── app/
│   ├── main.py                 # 🚀 Punto de entrada FastAPI
│   ├── schemas.py              # 📋 Modelos Pydantic (validación)
│   ├── core/
│   │   ├── config.py           # ⚙️  Configuración (settings)
│   │   └── security.py         # 🔐 JWT, contraseñas, autenticación
│   ├── database/
│   │   ├── database.py         # 🗄️  Conexión a BD
│   │   └── init_db.py          # 📊 Datos iniciales (seeding)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # 👤 Model de Usuario
│   │   ├── category.py         # 📂 Categorías de gastos
│   │   ├── income.py           # 💵 Ingresos
│   │   ├── expense.py          # 📉 Gastos
│   │   ├── budget.py           # 💰 Presupuestos
│   │   ├── debt.py             # 💳 Deudas (con start_date)
│   │   ├── debt_payment.py     # 📅 Cronograma de pagos
│   │   └── credit_card.py      # 💳 Tarjetas de crédito
│   └── routers/
│       ├── __init__.py
│       ├── auth.py             # 🔑 Login/Register
│       ├── health.py           # ❤️  Health check
│       ├── categories.py       # 📂 CRUD Categorías
│       ├── debts.py            # 💳 CRUD Deudas + Cronograma
│       ├── budgets.py          # 💰 CRUD Presupuestos
│       └── credit_cards.py     # 💳 CRUD Tarjetas
├── alembic/                    # 🔄 Migraciones (si usa Alembic)
├── .env.example                # 📝 Template variables entorno
├── .env                        # ⛔ Variables entorno (NO commitar)
├── requirements.txt            # 📦 Dependencias Python
├── run.py                      # 🏃 Script para ejecutar servidor
├── Dockerfile                  # 🐳 Configuración Docker
├── scripts/                    # 🧰 Scripts auxiliares
│   ├── create_debt_payments_table.py
│   ├── add_start_date_to_debts.py
│   └── ...otros scripts
└── README.md                   # 📖 Este archivo
```

## 📊 Modelos de Datos

### User (Usuario)

```python
{
  "id": 1,
  "email": "usuario@example.com",
  "password_hash": "hash_bcrypt",
  "created_at": "2026-02-12T10:00:00"
}
```

### Category (Categoría)

```python
{
  "id": 1,
  "name": "Alimentación",
  "icon": "🍔"
}
```

### Transaction (Transacción)

```python
{
  "id": 1,
  "user_id": 1,
  "type": "expense|income",
  "amount": 150.00,
  "category_id": 5,
  "date": "2026-02-12",
  "payment_method": "cash|credit_card",
  "credit_card_id": null,
  "description": "Compra en supermercado"
}
```

### Budget (Presupuesto)

```python
{
  "id": 1,
  "user_id": 1,
  "category_id": 5,
  "amount": 500.00,
  "month": "2026-02",
  "created_at": "2026-02-01T10:00:00"
}
```

### Debt (Deuda) ⭐

```python
{
  "id": 1,
  "user_id": 1,
  "creditor": "Banco Ejemplo",
  "total_amount": 5000.00,
  "paid_amount": 1500.00,
  "monthly_payment": 500.00,
  "start_date": "2026-03-15",      # 🆕 Cuándo empieza
  "due_date": "2026-12-15",        # Hasta cuándo
  "description": "Préstamo personal",
  "payments": [...]                # Cronograma de pagos
}
```

### DebtPayment (Cuota de Deuda) ⭐

```python
{
  "id": 1,
  "debt_id": 1,
  "due_date": "2026-03-15",
  "amount": 500.00,
  "is_paid": false,
  "paid_date": null
}
```

### CreditCard (Tarjeta de Crédito)

```python
{
  "id": 1,
  "user_id": 1,
  "name": "Visa Clásica",
  "credit_limit": 10000.00,
  "created_at": "2026-02-12T10:00:00"
}
```

## 🔗 Endpoints API

**Base URL:** `http://localhost:8000/api/v1`

### 🔐 Autenticación

```http
POST /auth/login
Content-Type: application/json

{
  "email": "admin@lumina.com",
  "password": "admin123"
}

RESPONSE 200:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

```http
POST /auth/register
Content-Type: application/json

{
  "email": "nuevo@example.com",
  "password": "contraseña123"
}

RESPONSE 201:
{
  "id": 5,
  "email": "nuevo@example.com",
  "created_at": "2026-02-12T10:00:00"
}
```

### 📂 Categorías

```http
GET /categories
Authorization: Bearer <token>

RESPONSE 200:
[
  {"id": 1, "name": "Salario", "icon": "💵"},
  {"id": 2, "name": "Alimentación", "icon": "🍔"}
]
```

### 💳 Deudas

```http
# Listar deudas
GET /debts?include_paid=false
Authorization: Bearer <token>

# Crear deuda
POST /debts
Authorization: Bearer <token>
Content-Type: application/json

{
  "creditor": "Banco XYZ",
  "total_amount": 5000,
  "monthly_payment": 500,
  "start_date": "2026-03-15",      # Cuándo empieza
  "due_date": "2026-12-15",        # Hasta cuándo
  "description": "Préstamo personal"
}

RESPONSE 201:
{
  "id": 1,
  "creditor": "Banco XYZ",
  ...
  "payments": [
    {
      "id": 1,
      "due_date": "2026-03-15",
      "amount": 500.00,
      "is_paid": false,
      "paid_date": null
    },
    ...más cuotas
  ]
}

# Marcar pago como realizado
POST /debts/payments/123/mark-paid
Authorization: Bearer <token>

{
  "paid_date": "2026-03-15"  # opcional, usa hoy si no se especifica
}

RESPONSE 200:
{
  "message": "Cuota marcada como pagada"
}
```

### 💰 Presupuestos

```http
# Listar presupuestos
GET /budgets
Authorization: Bearer <token>

# Crear presupuesto
POST /budgets
Authorization: Bearer <token>
Content-Type: application/json

{
  "category_id": 5,
  "amount": 500.00
}

# Actualizar presupuesto
PATCH /budgets/1
Authorization: Bearer <token>

{
  "amount": 600.00
}

# Eliminar presupuesto
DELETE /budgets/1
Authorization: Bearer <token>
```

### 💳 Tarjetas de Crédito

```http
# Listar tarjetas
GET /credit-cards
Authorization: Bearer <token>

# Crear tarjeta
POST /credit-cards
Authorization: Bearer <token>

{
  "name": "Visa Platinum",
  "credit_limit": 15000.00
}

# Eliminar tarjeta
DELETE /credit-cards/1
Authorization: Bearer <token>
```

### 💵 Transacciones

```http
# Listar transacciones
GET /transactions?start_date=2026-02-01&end_date=2026-02-28
Authorization: Bearer <token>

# Crear transacción
POST /transactions
Authorization: Bearer <token>

{
  "type": "expense",
  "amount": 150.00,
  "category_id": 5,
  "date": "2026-02-12",
  "payment_method": "credit_card",
  "credit_card_id": 1,
  "description": "Compra en supermercado"
}

# Eliminar transacción
DELETE /transactions/1
Authorization: Bearer <token>
```

## 🔐 Autenticación

### JWT (JSON Web Tokens)

La API usa tokens JWT para autenticación:

1. **Login**: POST `/auth/login` → recibe `access_token`
2. **Usar Token**: Incluir en headers: `Authorization: Bearer <token>`
3. **Expiración**: 30 minutos (configurable en `.env`)

### Headers Requeridos

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

### Ejemplo con cURL

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@lumina.com","password":"admin123"}'

# Usar token obtenido
curl -X GET http://localhost:8000/api/v1/debts \
  -H "Authorization: Bearer eyJhbGc..."
```

## 🔄 Migraciones

### Usando Scripts (Recomendado)

```bash
# Crear tabla debt_payments y agregar start_date
python scripts/create_debt_payments_table.py
python scripts/add_start_date_to_debts.py
```

### Usando Alembic (Opcional)

```bash
# Generar migración automática
alembic revision --autogenerate -m "descripcion cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1
```

## 💻 Desarrollo

### Hot Reload

FastAPI con uvicorn soporta hot reload. Cualquier cambio en el código se recarga automáticamente:

```bash
python run.py
# O
uvicorn app.main:app --reload
```

### Documentación Interactiva

FastAPI genera documentación automática:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Testing (Opcional)

```bash
# Instalar pytest
pip install pytest pytest-asyncio

# Ejecutar tests
pytest tests/
```

### Linting y Formatting

```bash
# Instalar herramientas
pip install black flake8

# Formatear código
black app/

# Revisar estilo
flake8 app/
```

## 🐛 Troubleshooting

### Error: "Connection to database failed"

**Causa**: PostgreSQL no está conectado o credenciales incorrectas

**Solución**:

```bash
# Verificar PostgreSQL está corriendo
psql -U postgres -h localhost

# Revisar credenciales en .env
# Crear BD si no existe
createdb -U postgres lumina_finance
```

### Error: "No module named 'app'"

**Causa**: Entorno virtual no activado

**Solución**:

```bash
# Windows
venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

### Error: "401 Unauthorized"

**Causa**: Token inválido o expirado

**Solución**:

```bash
# Hacer login nuevamente para obtener nuevo token
POST /auth/login
```

### Error: "CORS blocked"

**Solución**: En `app/main.py` verificar que CORS está configurado:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Migraciones fallando

```bash
# Recrear todas las tablas (⚠️ Borra datos)
python -c "from app.database.database import Base, engine; Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)"

# Reinsertar datos iniciales
python -c "from app.database.init_db import init_db; init_db()"
```

## 📚 Recursos Adicionales

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Pydantic v2](https://docs.pydantic.dev/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

## 📝 Notas Importantes

- **⛔ Nunca commitar `.env`**: Contiene secretos
- **🔐 Cambiar `SECRET_KEY`**: Usar valor único y seguro
- **📊 Backups**: Hacer backup de BD regularmente
- **🔄 Migraciones**: Aplicar migraciones antes de actualizar producción

## 📧 Soporte

- Issues: GitHub/issues
- Email: backend@luminafinance.com

---

**Última actualización**: Febrero 2026  
**Versión**: 1.0.0
