"""Product model definition."""
from decimal import Decimal
from typing import TYPE_CHECKING, List

from sqlalchemy import CheckConstraint, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.order import OrderItem


class Product(Base):
    """Product model representing items in inventory."""
    
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Database constraint to ensure non-negative stock
    __table_args__ = (
        CheckConstraint("stock_quantity >= 0", name="check_stock_non_negative"),
    )
    
    # Relationship to OrderItems
    order_items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="product"
    )
    
    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name='{self.name}', stock={self.stock_quantity})>"
