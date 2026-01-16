"""Order and OrderItem model definitions."""
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.enums import OrderStatus

if TYPE_CHECKING:
    from app.models.product import Product


class Order(Base):
    """Order model representing customer orders."""
    
    __tablename__ = "orders"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(),
        server_default=func.now(),
        nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default=OrderStatus.PENDING.value,
        nullable=False
    )
    
    # Relationship to OrderItems with eager loading
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Order(id={self.id}, status='{self.status}', items={len(self.items)})>"


class OrderItem(Base):
    """OrderItem model representing individual items within an order."""
    
    __tablename__ = "order_items"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_at_order: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Price of the product at the time of order"
    )
    
    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")
    
    def __repr__(self) -> str:
        return f"<OrderItem(id={self.id}, product_id={self.product_id}, quantity={self.quantity})>"
