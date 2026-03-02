from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import Base, engine
from app.database.init_db import create_database_if_not_exists
from app.routers import auth, budgets, categories, credit_cards, debts, health, reports
from app.transactions import router as transactions_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_database_if_not_exists()
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Finanzas API", lifespan=lifespan)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://finanzas-back-4k2g.onrender.com",
        "*",  # Permitir todos los orígenes en producción
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api/v1")


api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(budgets.router)
api_router.include_router(categories.router)
api_router.include_router(credit_cards.router)
api_router.include_router(debts.router)
api_router.include_router(reports.router)
api_router.include_router(transactions_router)
app.include_router(api_router)
