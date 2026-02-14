from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db
from app.models.debt import Debt
from app.models.debt_payment import DebtPayment
from app.models.user import User
from app.schemas import DebtCreate, DebtResponse, DebtUpdate

router = APIRouter(prefix="/debts", tags=["debts"])


@router.get("", response_model=list[DebtResponse])
def list_debts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    include_paid: bool = False,
):
    """Lista todas las deudas del usuario"""
    query = db.query(Debt).filter(Debt.user_id == current_user.id)

    if not include_paid:
        # Solo mostrar deudas no pagadas completamente
        query = query.filter(Debt.paid_amount < Debt.total_amount)

    debts = query.order_by(Debt.due_date.asc().nullslast(), Debt.id.desc()).all()
    return debts


@router.get("/{debt_id}", response_model=DebtResponse)
def get_debt(
    debt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene una deuda específica"""
    debt = (
        db.query(Debt)
        .filter(Debt.id == debt_id, Debt.user_id == current_user.id)
        .first()
    )

    if not debt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deuda no encontrada",
        )

    return debt


@router.post("", response_model=DebtResponse, status_code=status.HTTP_201_CREATED)
def create_debt(
    payload: DebtCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Crea una nueva deuda"""
    debt = Debt(
        user_id=current_user.id,
        creditor=payload.creditor,
        total_amount=payload.total_amount,
        paid_amount=Decimal("0.00"),
        monthly_payment=payload.monthly_payment,
        start_date=payload.start_date,
        due_date=payload.due_date,
        description=payload.description,
    )

    db.add(debt)
    db.commit()
    db.refresh(debt)

    # Si tiene cuota mensual, fecha de inicio y fecha de vencimiento, generar cronograma
    if payload.monthly_payment and payload.start_date and payload.due_date:
        generate_payment_schedule(
            db, debt, payload.monthly_payment, payload.start_date, payload.due_date
        )

    return debt


@router.patch("/{debt_id}", response_model=DebtResponse)
def update_debt(
    debt_id: int,
    payload: DebtUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Actualiza una deuda"""
    debt = (
        db.query(Debt)
        .filter(Debt.id == debt_id, Debt.user_id == current_user.id)
        .first()
    )

    if not debt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deuda no encontrada",
        )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(debt, field, value)

    db.commit()
    db.refresh(debt)

    return debt


def generate_payment_schedule(
    db: Session,
    debt: Debt,
    monthly_payment: Decimal,
    start_date: date,
    final_due_date: date,
):
    """Genera el cronograma de pagos mensuales para una deuda"""
    current_date = start_date
    remaining = Decimal(str(debt.total_amount))

    while remaining > 0 and current_date <= final_due_date:
        # Si es la última cuota, ajustar monto
        payment_amount = min(monthly_payment, remaining)

        payment = DebtPayment(
            debt_id=debt.id,
            due_date=current_date,
            amount=payment_amount,
            is_paid=False,
        )
        db.add(payment)

        remaining -= payment_amount
        current_date = current_date + timedelta(days=30)  # Aproximado mensual

    db.commit()


class MarkPaymentPaid(BaseModel):
    paid_date: date | None = None


@router.post("/payments/{payment_id}/mark-paid")
def mark_payment_as_paid(
    payment_id: int,
    payload: MarkPaymentPaid,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Marca una cuota como pagada"""
    payment = (
        db.query(DebtPayment)
        .join(Debt)
        .filter(
            DebtPayment.id == payment_id,
            Debt.user_id == current_user.id,
        )
        .first()
    )

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cuota no encontrada",
        )

    if payment.is_paid:  # type: ignore[attr-defined]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta cuota ya está marcada como pagada",
        )

    # Marcar como pagada
    payment.is_paid = True  # type: ignore[assignment]
    payment.paid_date = payload.paid_date or date.today()  # type: ignore[assignment]

    # Actualizar paid_amount de la deuda
    debt = db.query(Debt).filter(Debt.id == payment.debt_id).first()  # type: ignore[attr-defined]
    if debt:
        debt.paid_amount = Decimal(str(debt.paid_amount)) + Decimal(str(payment.amount))  # type: ignore[assignment, attr-defined]

    db.commit()

    return {"message": "Cuota marcada como pagada"}


@router.delete("/{debt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_debt(
    debt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina una deuda"""
    debt = (
        db.query(Debt)
        .filter(Debt.id == debt_id, Debt.user_id == current_user.id)
        .first()
    )

    if not debt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deuda no encontrada",
        )

    db.delete(debt)
    db.commit()
