from __future__ import annotations

from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.sql import ColumnElement
from typing import Any
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db
from app.models.expense import Expense
from app.models.income import Income
from app.models.user import User
from pydantic import BaseModel


class MonthlyReport(BaseModel):
    year: int
    month: int
    month_name: str
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal
    is_positive: bool


router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/monthly", response_model=list[MonthlyReport])
def get_monthly_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    year: int | None = Query(default=None, ge=2000, le=2100),
):
    """Obtiene el reporte mensual de ingresos y gastos"""

    # Si no se especifica año, usar el año actual
    if year is None:
        year = date.today().year

    # Consulta de ingresos por mes
    income_date_col: ColumnElement[Any] = Income.__table__.c.date
    income_query = (
        select(
            func.extract("month", income_date_col).label("month"),
            func.coalesce(func.sum(Income.amount), 0).label("total_income"),
        )
        .where(
            Income.user_id == current_user.id,
            func.extract("year", income_date_col) == year,
        )
        .group_by(func.extract("month", income_date_col))
    )

    # Consulta de gastos por mes
    expense_date_col: ColumnElement[Any] = Expense.__table__.c.date
    expense_query = (
        select(
            func.extract("month", expense_date_col).label("month"),
            func.coalesce(func.sum(Expense.amount), 0).label("total_expense"),
        )
        .where(
            Expense.user_id == current_user.id,
            func.extract("year", expense_date_col) == year,
        )
        .group_by(func.extract("month", expense_date_col))
    )

    # Ejecutar consultas
    income_results = {
        int(row.month): Decimal(str(row.total_income))
        for row in db.execute(income_query).all()
    }
    expense_results = {
        int(row.month): Decimal(str(row.total_expense))
        for row in db.execute(expense_query).all()
    }

    # Nombres de meses en español
    month_names = [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre",
    ]

    # Construir reporte para los 12 meses
    reports: list[MonthlyReport] = []
    for month_num in range(1, 13):
        total_income = income_results.get(month_num, Decimal("0"))
        total_expense = expense_results.get(month_num, Decimal("0"))
        balance = total_income - total_expense

        reports.append(
            MonthlyReport(
                year=year,
                month=month_num,
                month_name=month_names[month_num - 1],
                total_income=total_income,
                total_expense=total_expense,
                balance=balance,
                is_positive=balance >= 0,
            )
        )

    return reports
