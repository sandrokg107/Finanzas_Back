from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.database import get_db
from app.models.credit_card import CreditCard
from app.models.user import User


class CreditCardCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    credit_limit: Decimal = Field(gt=0)
    closing_day: int = Field(ge=1, le=31)


class CreditCardUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    credit_limit: Decimal | None = Field(default=None, gt=0)
    closing_day: int | None = Field(default=None, ge=1, le=31)


class CreditCardResponse(BaseModel):
    id: int
    name: str
    credit_limit: Decimal
    used_amount: Decimal
    available_amount: Decimal
    closing_day: int

    model_config = {"from_attributes": True}


router = APIRouter(prefix="/credit-cards", tags=["credit-cards"])


@router.get("", response_model=list[CreditCardResponse])
def list_credit_cards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene todas las tarjetas de crédito del usuario"""
    cards = (
        db.query(CreditCard)
        .filter(CreditCard.user_id == current_user.id)
        .order_by(CreditCard.name)
        .all()
    )

    return [
        CreditCardResponse(
            id=card.id,
            name=card.name,
            credit_limit=card.credit_limit,
            used_amount=card.used_amount,
            available_amount=card.available_amount,
            closing_day=card.closing_day,
        )
        for card in cards
    ]


@router.post("", response_model=CreditCardResponse)
def create_credit_card(
    payload: CreditCardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Crea una nueva tarjeta de crédito"""

    card = CreditCard(
        user_id=current_user.id,
        name=payload.name,
        credit_limit=payload.credit_limit,
        used_amount=Decimal("0"),
        closing_day=payload.closing_day,
    )

    db.add(card)
    db.commit()
    db.refresh(card)

    return CreditCardResponse(
        id=card.id,
        name=card.name,
        credit_limit=card.credit_limit,
        used_amount=card.used_amount,
        available_amount=card.available_amount,
        closing_day=card.closing_day,
    )


@router.patch("/{card_id}", response_model=CreditCardResponse)
def update_credit_card(
    card_id: int,
    payload: CreditCardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Actualiza una tarjeta de crédito"""

    card = (
        db.query(CreditCard)
        .filter(CreditCard.id == card_id, CreditCard.user_id == current_user.id)
        .first()
    )

    if not card:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada")

    if payload.name is not None:
        card.name = payload.name  # type: ignore[assignment]
    if payload.credit_limit is not None:
        card.credit_limit = payload.credit_limit  # type: ignore[assignment]
    if payload.closing_day is not None:
        card.closing_day = payload.closing_day  # type: ignore[assignment]

    db.commit()
    db.refresh(card)

    return CreditCardResponse(
        id=card.id,
        name=card.name,
        credit_limit=card.credit_limit,
        used_amount=card.used_amount,
        available_amount=card.available_amount,
        closing_day=card.closing_day,
    )


@router.delete("/{card_id}")
def delete_credit_card(
    card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina una tarjeta de crédito"""

    card = (
        db.query(CreditCard)
        .filter(CreditCard.id == card_id, CreditCard.user_id == current_user.id)
        .first()
    )

    if not card:
        raise HTTPException(status_code=404, detail="Tarjeta no encontrada")

    if card.used_amount > 0:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar una tarjeta con saldo usado. Paga primero.",
        )

    db.delete(card)
    db.commit()

    return {"message": "Tarjeta eliminada"}
