from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class DebtPayment(Base):
    __tablename__ = "debt_payments"

    id = Column(Integer, primary_key=True, index=True)
    debt_id = Column(
        Integer, ForeignKey("debts.id", ondelete="CASCADE"), nullable=False
    )
    due_date = Column(Date, nullable=False)  # Fecha de vencimiento de la cuota
    amount = Column(Numeric(12, 2), nullable=False)  # Monto de la cuota
    is_paid = Column(Boolean, nullable=False, default=False)
    paid_date = Column(Date, nullable=True)  # Fecha real de pago
    was_late = Column(Boolean, nullable=False, default=False)  # Si se pagó tarde
    payment_method = Column(
        String(50), nullable=True
    )  # Efectivo, Tarjeta, Transferencia, etc.
    voucher_filename = Column(String(255), nullable=True)  # Nombre original del archivo
    voucher_path = Column(String(512), nullable=True)  # Ruta del archivo almacenado

    # Relationships
    debt = relationship("Debt", back_populates="payments")
