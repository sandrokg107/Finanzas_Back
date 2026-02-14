from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class CreditCard(Base):
    __tablename__ = "credit_cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # "Visa", "MasterCard", etc.
    credit_limit: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    used_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0")
    )
    closing_day: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # Día del mes (1-31)

    # Relationships
    user = relationship("User")

    @property
    def available_amount(self) -> Decimal:
        return self.credit_limit - self.used_amount
