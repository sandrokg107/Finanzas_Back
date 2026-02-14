from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import and_, func, select
from sqlalchemy.sql import ColumnElement
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db
from app.models.budget import Budget
from app.models.category import Category
from app.models.expense import Expense
from app.models.user import User


class BudgetCreate(BaseModel):
    category_id: int
    amount: Decimal = Field(gt=0)
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000, le=2100)


class BudgetUpdate(BaseModel):
    amount: Decimal = Field(gt=0)


class BudgetWithSpending(BaseModel):
    id: int
    category_id: int
    category_name: str
    amount: Decimal
    spent: Decimal
    remaining: Decimal
    percentage: float
    month: int
    year: int

    model_config = {"from_attributes": True}


router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.get("", response_model=list[BudgetWithSpending])
def list_budgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    month: int | None = None,
    year: int | None = None,
):
    """Obtiene los presupuestos del usuario con el gasto actual"""
    from datetime import date

    # Si no se especifica mes/año, usar el actual
    if not month or not year:
        today = date.today()
        month = month or today.month
        year = year or today.year

    # Obtener presupuestos
    budgets_query = (
        select(Budget, Category.name)
        .join(Category, Budget.category_id == Category.id)
        .where(
            Budget.user_id == current_user.id,
            Budget.month == month,
            Budget.year == year,
        )
    )

    budgets = db.execute(budgets_query).all()

    result: list[BudgetWithSpending] = []
    date_col: ColumnElement[Any] = Expense.__table__.c.date
    for budget, category_name in budgets:
        # Calcular gasto actual para esta categoría en este mes/año
        spent_query = select(func.coalesce(func.sum(Expense.amount), 0)).where(
            and_(
                Expense.user_id == current_user.id,
                Expense.category_id == budget.category_id,
                func.extract("month", date_col) == month,
                func.extract("year", date_col) == year,
            )
        )

        spent = Decimal(str(db.execute(spent_query).scalar() or 0))
        amount = budget.amount
        remaining = amount - spent
        percentage = float((spent / amount * 100) if amount > 0 else 0)

        result.append(
            BudgetWithSpending(
                id=budget.id,
                category_id=budget.category_id,
                category_name=category_name,
                amount=amount,
                spent=spent,
                remaining=remaining,
                percentage=min(percentage, 100),
                month=budget.month,
                year=budget.year,
            )
        )

    return result


@router.post("", response_model=BudgetWithSpending)
def create_budget(
    payload: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Crea un nuevo presupuesto"""

    # Verificar que la categoría existe
    category = db.query(Category).filter(Category.id == payload.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    # Verificar que no exista ya un presupuesto para esta categoría/mes/año
    existing = (
        db.query(Budget)
        .filter(
            Budget.user_id == current_user.id,
            Budget.category_id == payload.category_id,
            Budget.month == payload.month,
            Budget.year == payload.year,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un presupuesto para esta categoría en este mes",
        )

    budget = Budget(
        user_id=current_user.id,
        category_id=payload.category_id,
        amount=payload.amount,
        month=payload.month,
        year=payload.year,
    )

    db.add(budget)
    db.commit()
    db.refresh(budget)

    # Calcular spending para respuesta
    date_col: ColumnElement[Any] = Expense.__table__.c.date
    spent_query = select(func.coalesce(func.sum(Expense.amount), 0)).where(
        and_(
            Expense.user_id == current_user.id,
            Expense.category_id == budget.category_id,
            func.extract("month", date_col) == payload.month,
            func.extract("year", date_col) == payload.year,
        )
    )

    spent = Decimal(str(db.execute(spent_query).scalar() or 0))
    amount = budget.amount
    remaining = amount - spent
    percentage = float((spent / amount * 100) if amount > 0 else 0)
    category_name = category.name

    return BudgetWithSpending(
        id=budget.id,
        category_id=budget.category_id,
        category_name=category_name,
        amount=amount,
        spent=spent,
        remaining=remaining,
        percentage=min(percentage, 100),
        month=budget.month,
        year=budget.year,
    )


@router.patch("/{budget_id}", response_model=BudgetWithSpending)
def update_budget(
    budget_id: int,
    payload: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Actualiza el monto de un presupuesto"""

    budget = (
        db.query(Budget)
        .filter(Budget.id == budget_id, Budget.user_id == current_user.id)
        .first()
    )

    if not budget:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")

    budget.amount = payload.amount  # type: ignore[assignment]
    db.commit()
    db.refresh(budget)

    # Obtener categoría
    category = db.query(Category).filter(Category.id == budget.category_id).first()

    # Calcular spending
    date_col: ColumnElement[Any] = Expense.__table__.c.date
    spent_query = select(func.coalesce(func.sum(Expense.amount), 0)).where(
        and_(
            Expense.user_id == current_user.id,
            Expense.category_id == budget.category_id,
            func.extract("month", date_col) == budget.month,
            func.extract("year", date_col) == budget.year,
        )
    )

    spent = Decimal(str(db.execute(spent_query).scalar() or 0))
    amount = budget.amount
    remaining = amount - spent
    percentage = float((spent / amount * 100) if amount > 0 else 0)

    return BudgetWithSpending(
        id=budget.id,
        category_id=budget.category_id,
        category_name=category.name if category else "",
        amount=amount,
        spent=spent,
        remaining=remaining,
        percentage=min(percentage, 100),
        month=budget.month,
        year=budget.year,
    )


@router.delete("/{budget_id}")
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina un presupuesto"""

    budget = (
        db.query(Budget)
        .filter(Budget.id == budget_id, Budget.user_id == current_user.id)
        .first()
    )

    if not budget:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")

    db.delete(budget)
    db.commit()

    return {"message": "Presupuesto eliminado"}
