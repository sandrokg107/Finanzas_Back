from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, EmailStr, Field
from pydantic.config import ConfigDict


class TransactionCreate(BaseModel):
    type: Literal["income", "expense"]
    amount: Decimal = Field(gt=0)
    description: str | None = None
    date: date
    category_id: int
    debt_id: int | None = None  # Para vincular con una deuda
    payment_method: Literal["cash", "credit_card"] = "cash"
    credit_card_id: int | None = None  # Requerido si payment_method='credit_card'


class TransactionResponse(BaseModel):
    id: int
    type: Literal["income", "expense"]
    amount: Decimal
    description: str | None = None
    date: date
    category_id: int
    payment_method: str | None = None
    credit_card_id: int | None = None
    category_id: int

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DashboardSummary(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal


class DebtCreate(BaseModel):
    creditor: str
    total_amount: Decimal = Field(gt=0)
    monthly_payment: Decimal | None = Field(default=None, gt=0)  # Cuota mensual
    start_date: date | None = None  # Fecha de inicio de pagos
    due_date: date | None = None  # Fecha de vencimiento final
    description: str | None = None


class DebtUpdate(BaseModel):
    creditor: str | None = None
    total_amount: Decimal | None = Field(default=None, gt=0)
    monthly_payment: Decimal | None = Field(default=None, gt=0)
    start_date: date | None = None
    due_date: date | None = None
    description: str | None = None


class DebtPaymentResponse(BaseModel):
    id: int
    debt_id: int
    due_date: date
    amount: Decimal
    is_paid: bool
    paid_date: date | None

    model_config = ConfigDict(from_attributes=True)


class DebtResponse(BaseModel):
    id: int
    user_id: int
    creditor: str
    total_amount: Decimal
    paid_amount: Decimal
    monthly_payment: Decimal | None
    start_date: date | None
    due_date: date | None
    description: str | None
    payments: list[DebtPaymentResponse] = []

    model_config = ConfigDict(from_attributes=True)
