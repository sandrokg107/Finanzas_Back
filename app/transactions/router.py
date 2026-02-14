from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, literal, select
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db
from app.models.credit_card import CreditCard
from app.models.expense import Expense
from app.models.income import Income
from app.models.user import User
from app.models.debt import Debt
from app.models.debt_payment import DebtPayment
from app.schemas import DashboardSummary, TransactionCreate, TransactionResponse

router = APIRouter(tags=["transactions"])


@router.get("/transactions", response_model=list[TransactionResponse])
def list_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    month: int | None = Query(default=None, ge=1, le=12),
    year: int | None = Query(default=None, ge=2000, le=2100),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=500),
) -> list[TransactionResponse]:
    income_query = select(
        Income.id.label("id"),
        Income.amount.label("amount"),
        Income.description.label("description"),
        Income.date.label("date"),
        Income.category_id.label("category_id"),
        literal("income").label("type"),
    ).where(Income.user_id == current_user.id)

    if month is not None:
        income_query = income_query.where(func.extract("month", Income.date) == month)
    if year is not None:
        income_query = income_query.where(func.extract("year", Income.date) == year)

    expense_query = select(
        Expense.id.label("id"),
        Expense.amount.label("amount"),
        Expense.description.label("description"),
        Expense.date.label("date"),
        Expense.category_id.label("category_id"),
        literal("expense").label("type"),
    ).where(Expense.user_id == current_user.id)

    if month is not None:
        expense_query = expense_query.where(
            func.extract("month", Expense.date) == month
        )
    if year is not None:
        expense_query = expense_query.where(func.extract("year", Expense.date) == year)

    union_query = income_query.union_all(expense_query).subquery()
    ordered = (
        select(union_query)
        .order_by(union_query.c.date.desc(), union_query.c.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    rows = db.execute(ordered).mappings().all()
    return [TransactionResponse(**row) for row in rows]


@router.post("/transactions", response_model=TransactionResponse)
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TransactionResponse:
    # Si se vincula con una deuda, validar y actualizar
    if payload.debt_id:
        debt = (
            db.query(Debt)
            .filter(Debt.id == payload.debt_id, Debt.user_id == current_user.id)
            .first()
        )

        if not debt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deuda no encontrada",
            )

        # Calcular nuevo monto pagado
        new_paid_amount = Decimal(str(debt.paid_amount)) + payload.amount

        # Asegurar que no se pague más del total
        if new_paid_amount > Decimal(str(debt.total_amount)):
            remaining = Decimal(str(debt.total_amount)) - Decimal(str(debt.paid_amount))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El pago excede el monto total de la deuda. Restante: {remaining}",
            )

        # Aplicar el pago al cronograma si existe
        pending_payments = (
            db.query(DebtPayment)
            .filter(DebtPayment.debt_id == debt.id, DebtPayment.is_paid.is_(False))
            .order_by(DebtPayment.due_date.asc(), DebtPayment.id.asc())
            .all()
        )

        if pending_payments:
            remaining = Decimal(str(payload.amount))
            applied_amount = Decimal("0")

            for payment in pending_payments:
                if remaining <= 0:
                    break

                payment_amount = Decimal(str(payment.amount))
                if remaining >= payment_amount:
                    payment.is_paid = True  # type: ignore[assignment]
                    payment.paid_date = payload.date  # type: ignore[assignment]
                    remaining -= payment_amount
                    applied_amount += payment_amount

            # Si sobra monto, registrar como pago extra ya realizado
            if remaining > 0:
                extra_payment = DebtPayment(
                    debt_id=debt.id,
                    due_date=payload.date,
                    amount=remaining,
                    is_paid=True,
                    paid_date=payload.date,
                )
                db.add(extra_payment)
                applied_amount += remaining

            debt.paid_amount = Decimal(str(debt.paid_amount)) + applied_amount  # type: ignore[assignment]
        else:
            # Sin cronograma, solo acumular en paid_amount
            debt.paid_amount = new_paid_amount  # type: ignore[assignment]

    if payload.type == "income":
        item = Income(
            amount=payload.amount,
            description=payload.description,
            date=payload.date,
            category_id=payload.category_id,
            user_id=current_user.id,
        )
    else:
        # Validar tarjeta si se usa payment_method='credit_card'
        if payload.payment_method == "credit_card":
            if not payload.credit_card_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Debe especificar una tarjeta de crédito",
                )

            card = (
                db.query(CreditCard)
                .filter(
                    CreditCard.id == payload.credit_card_id,
                    CreditCard.user_id == current_user.id,
                )
                .first()
            )

            if not card:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tarjeta no encontrada",
                )

            # Validar límite disponible
            if card.used_amount + payload.amount > card.credit_limit:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Límite de crédito excedido. Disponible: {card.available_amount}",
                )

            # Aumentar saldo usado
            card.used_amount = card.used_amount + payload.amount  # type: ignore[assignment]

        item = Expense(
            amount=payload.amount,
            description=payload.description,
            date=payload.date,
            category_id=payload.category_id,
            user_id=current_user.id,
            payment_method=payload.payment_method,
            credit_card_id=payload.credit_card_id,
        )

    db.add(item)
    db.commit()
    db.refresh(item)

    return TransactionResponse(
        id=item.id,
        type=payload.type,
        amount=item.amount,
        description=item.description,
        date=item.date,
        category_id=item.category_id,
        payment_method=getattr(item, "payment_method", None),
        credit_card_id=getattr(item, "credit_card_id", None),
    )


@router.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    income = (
        db.query(Income)
        .filter(Income.id == transaction_id, Income.user_id == current_user.id)
        .first()
    )
    if income:
        db.delete(income)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    expense = (
        db.query(Expense)
        .filter(Expense.id == transaction_id, Expense.user_id == current_user.id)
        .first()
    )
    if expense:
        db.delete(expense)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")


@router.get("/dashboard/summary", response_model=DashboardSummary)
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    month: int | None = Query(default=None, ge=1, le=12),
    year: int | None = Query(default=None, ge=2000, le=2100),
) -> DashboardSummary:
    income_query = select(func.coalesce(func.sum(Income.amount), 0)).where(
        Income.user_id == current_user.id
    )
    expense_query = select(func.coalesce(func.sum(Expense.amount), 0)).where(
        Expense.user_id == current_user.id
    )

    if month is not None:
        income_query = income_query.where(func.extract("month", Income.date) == month)
        expense_query = expense_query.where(
            func.extract("month", Expense.date) == month
        )
    if year is not None:
        income_query = income_query.where(func.extract("year", Income.date) == year)
        expense_query = expense_query.where(func.extract("year", Expense.date) == year)

    total_income = db.execute(income_query).scalar_one()
    total_expense = db.execute(expense_query).scalar_one()
    balance = Decimal(total_income) - Decimal(total_expense)

    return DashboardSummary(
        total_income=Decimal(total_income),
        total_expense=Decimal(total_expense),
        balance=balance,
    )
