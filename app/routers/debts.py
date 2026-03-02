from __future__ import annotations

import os
import uuid
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db
from app.models.category import Category
from app.models.debt import Debt
from app.models.debt_payment import DebtPayment
from app.models.expense import Expense
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


class PaymentReminderResponse(BaseModel):
    debt_id: int
    debt_creditor: str
    payment_id: int
    payment_amount: Decimal
    due_date: date
    days_until_due: int
    is_overdue: bool


@router.get("/reminders/upcoming", response_model=list[PaymentReminderResponse])
def get_payment_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene los pagos próximos a vencer según los días de recordatorio configurados"""
    today = date.today()

    # Obtener todas las deudas activas del usuario
    debts = (
        db.query(Debt)
        .filter(
            Debt.user_id == current_user.id,
            Debt.paid_amount < Debt.total_amount,
        )
        .all()
    )

    reminders = []

    for debt in debts:
        reminder_days = debt.reminder_days or 3
        future_date = today + timedelta(days=reminder_days)

        # Obtener pagos pendientes que vencen dentro del rango de recordatorio
        for payment in debt.payments:
            if not payment.is_paid:
                days_diff = (payment.due_date - today).days

                # Incluir si está vencido o próximo a vencer
                if days_diff <= reminder_days:
                    reminders.append(
                        PaymentReminderResponse(
                            debt_id=debt.id,
                            debt_creditor=debt.creditor,
                            payment_id=payment.id,
                            payment_amount=payment.amount,
                            due_date=payment.due_date,
                            days_until_due=days_diff,
                            is_overdue=days_diff < 0,
                        )
                    )

    # Ordenar por días hasta vencimiento (vencidos primero)
    reminders.sort(key=lambda x: x.days_until_due)

    return reminders


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
        total_installments=payload.total_installments,
        payment_day=payload.payment_day,
        start_date=payload.start_date,
        due_date=payload.due_date,
        reminder_days=payload.reminder_days or 3,
        description=payload.description,
    )

    db.add(debt)
    db.commit()
    db.refresh(debt)

    # Si tiene cuota mensual y fecha de inicio, generar cronograma
    if payload.monthly_payment and payload.start_date:
        # Usar total_installments si está disponible, sino calcular por fecha
        if payload.total_installments:
            generate_payment_schedule_by_installments(
                db,
                debt,
                payload.monthly_payment,
                payload.start_date,
                payload.total_installments,
            )
        elif payload.due_date:
            generate_payment_schedule_by_date(
                db, debt, payload.monthly_payment, payload.start_date, payload.due_date
            )

        # Si se indicó cuotas ya pagadas, marcarlas automáticamente
        if payload.paid_installments_count and payload.paid_installments_count > 0:
            payments = (
                db.query(DebtPayment)
                .filter(DebtPayment.debt_id == debt.id)
                .order_by(DebtPayment.due_date)
                .limit(payload.paid_installments_count)
                .all()
            )

            total_paid = Decimal("0.00")
            for payment in payments:
                payment.is_paid = True
                payment.paid_date = (
                    payment.due_date
                )  # Usar la fecha de vencimiento como fecha de pago
                total_paid += payment.amount

            # Actualizar el monto pagado de la deuda
            debt.paid_amount = total_paid
            db.commit()
            db.refresh(debt)

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


def generate_payment_schedule_by_installments(
    db: Session,
    debt: Debt,
    monthly_payment: Decimal,
    start_date: date,
    total_installments: int,
):
    """Genera el cronograma de pagos basado en número de cuotas"""
    current_date = start_date
    remaining = Decimal(str(debt.total_amount))

    # Usar payment_day si está disponible, sino usar el día de start_date
    payment_day = debt.payment_day if debt.payment_day else start_date.day

    for i in range(total_installments):
        # Si es la última cuota, ajustar monto al saldo restante
        if i == total_installments - 1:
            payment_amount = remaining
        else:
            payment_amount = min(monthly_payment, remaining)

        # Calcular la fecha de vencimiento manteniendo el día del mes
        if i > 0:
            current_date = start_date + relativedelta(months=i)
            # Ajustar al día de pago especificado
            try:
                current_date = current_date.replace(day=payment_day)
            except ValueError:
                # Si el día no existe en ese mes (ej: 31 en febrero), usar último día
                current_date = current_date.replace(day=1) + relativedelta(
                    months=1, days=-1
                )

        payment = DebtPayment(
            debt_id=debt.id,
            due_date=current_date,
            amount=payment_amount,
            is_paid=False,
        )
        db.add(payment)

        remaining -= payment_amount
        if remaining <= 0:
            break

    db.commit()


def generate_payment_schedule_by_date(
    db: Session,
    debt: Debt,
    monthly_payment: Decimal,
    start_date: date,
    final_due_date: date,
):
    """Genera el cronograma de pagos basado en fecha final"""
    current_date = start_date
    remaining = Decimal(str(debt.total_amount))

    # Usar payment_day si está disponible, sino usar el día de start_date
    payment_day = debt.payment_day if debt.payment_day else start_date.day
    month_count = 0

    while remaining > 0 and current_date <= final_due_date:
        # Si es la primera iteración o calcular siguiente mes
        if month_count > 0:
            current_date = start_date + relativedelta(months=month_count)
            # Ajustar al día de pago especificado
            try:
                current_date = current_date.replace(day=payment_day)
            except ValueError:
                # Si el día no existe en ese mes, usar último día
                current_date = current_date.replace(day=1) + relativedelta(
                    months=1, days=-1
                )

        # Si pasamos la fecha límite, ajustar
        if current_date > final_due_date:
            current_date = final_due_date

        # Calcular monto del pago
        payment_amount = min(monthly_payment, remaining)

        payment = DebtPayment(
            debt_id=debt.id,
            due_date=current_date,
            amount=payment_amount,
            is_paid=False,
        )
        db.add(payment)

        remaining -= payment_amount
        month_count += 1

    db.commit()


class MarkPaymentPaid(BaseModel):
    paid_date: date | None = None
    payment_method: str | None = None  # Efectivo, Tarjeta, Transferencia, etc.


@router.post("/payments/{payment_id}/mark-paid")
def mark_payment_as_paid(
    payment_id: int,
    payload: MarkPaymentPaid,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Marca una cuota como pagada, permitiendo registrar pagos atrasados"""
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

    # Obtener fecha de pago (usar fecha actual si no se especifica)
    payment_date = payload.paid_date or date.today()

    # Determinar si el pago fue tardío
    was_late = payment_date > payment.due_date  # type: ignore[attr-defined]

    # Marcar como pagada
    payment.is_paid = True  # type: ignore[assignment]
    payment.paid_date = payment_date  # type: ignore[assignment]
    payment.was_late = was_late  # type: ignore[assignment]
    if payload.payment_method:
        payment.payment_method = payload.payment_method  # type: ignore[assignment]

    # Actualizar paid_amount de la deuda
    debt = db.query(Debt).filter(Debt.id == payment.debt_id).first()  # type: ignore[attr-defined]
    if debt:
        debt.paid_amount = Decimal(str(debt.paid_amount)) + Decimal(str(payment.amount))  # type: ignore[assignment, attr-defined]

        # Registrar el pago como gasto en transacciones
        category = db.query(Category).filter(Category.name == "Deudas").first()
        if not category:
            category = Category(name="Deudas")
            db.add(category)
            db.flush()

        expense = Expense(
            amount=Decimal(str(payment.amount)),
            description=f"Pago de deuda: {debt.creditor}",
            date=payment_date,
            category_id=category.id,
            user_id=current_user.id,
            payment_method="cash",
        )
        db.add(expense)

    db.commit()

    return {
        "message": "Cuota marcada como pagada",
        "was_late": was_late,
        "paid_date": payment_date.isoformat(),
    }


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


# Directorio para almacenar comprobantes
VOUCHERS_DIR = Path("uploads/vouchers")
VOUCHERS_DIR.mkdir(parents=True, exist_ok=True)

# Extensiones permitidas
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}


@router.post("/payments/{payment_id}/upload-voucher")
async def upload_payment_voucher(
    payment_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Subir comprobante de pago (PDF o imagen)"""
    # Verificar que el pago existe y pertenece al usuario
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

    if not payment.is_paid:  # type: ignore[attr-defined]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden subir comprobantes para pagos marcados como pagados",
        )

    # Validar extensión del archivo
    file_ext = os.path.splitext(file.filename or "")[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no permitido. Usa: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Generar nombre único para el archivo
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = VOUCHERS_DIR / unique_filename

    # Guardar archivo
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar el archivo: {str(e)}",
        )

    # Actualizar registro en base de datos
    payment.voucher_filename = file.filename  # type: ignore[assignment]
    payment.voucher_path = str(file_path)  # type: ignore[assignment]
    db.commit()

    return {
        "message": "Comprobante subido exitosamente",
        "filename": file.filename,
        "voucher_id": payment_id,
    }


@router.get("/payments/{payment_id}/download-voucher")
def download_payment_voucher(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Descargar comprobante de pago"""
    # Verificar que el pago existe y pertenece al usuario
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

    if not payment.voucher_path:  # type: ignore[attr-defined]
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay comprobante para este pago",
        )

    file_path = Path(payment.voucher_path)  # type: ignore[arg-type]
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo de comprobante no encontrado",
        )

    return FileResponse(
        path=file_path,
        filename=payment.voucher_filename or "comprobante",  # type: ignore[arg-type]
        media_type="application/octet-stream",
    )


@router.delete(
    "/payments/{payment_id}/delete-voucher", status_code=status.HTTP_204_NO_CONTENT
)
def delete_payment_voucher(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Eliminar comprobante de pago"""
    # Verificar que el pago existe y pertenece al usuario
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

    if not payment.voucher_path:  # type: ignore[attr-defined]
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay comprobante para eliminar",
        )

    # Eliminar archivo físico
    file_path = Path(payment.voucher_path)  # type: ignore[arg-type]
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception:
            pass  # Continuar incluso si no se puede eliminar el archivo

    # Limpiar campos en base de datos
    payment.voucher_filename = None  # type: ignore[assignment]
    payment.voucher_path = None  # type: ignore[assignment]
    db.commit()
