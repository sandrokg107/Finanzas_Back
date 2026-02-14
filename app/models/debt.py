from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class Debt(Base):
    __tablename__ = "debts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    creditor = Column(String, nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    paid_amount = Column(Numeric(12, 2), nullable=False, default=0)
    monthly_payment = Column(Numeric(12, 2), nullable=True)  # Cuota mensual
    start_date = Column(Date, nullable=True)  # Fecha de inicio de pagos
    due_date = Column(Date, nullable=True)  # Fecha de vencimiento final
    description = Column(String, nullable=True)

    # Relationships
    payments = relationship(
        "DebtPayment", back_populates="debt", cascade="all, delete-orphan"
    )
