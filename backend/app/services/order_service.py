"""Order service with transactional business logic."""
from typing import Dict, Set

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.exceptions import (
    InsufficientStockError,
    InvalidStatusTransitionError,
    OrderNotFoundError,
    ProductNotFoundError,
)
from app.models.enums import OrderStatus
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate


# Valid status transitions (state machine)
VALID_TRANSITIONS: Dict[OrderStatus, Set[OrderStatus]] = {
    OrderStatus.PENDING: {OrderStatus.SHIPPED, OrderStatus.CANCELLED},
    OrderStatus.SHIPPED: set(),  # Terminal state
    OrderStatus.CANCELLED: set(),  # Terminal state
}


class OrderService:
    """Service class for order-related operations."""
    
    @staticmethod
    async def create_order(db: AsyncSession, order_data: OrderCreate) -> Order:
        """
        Create a new order with atomic stock management.
        
        Uses SELECT FOR UPDATE to prevent race conditions during concurrent
        order processing. This ensures that:
        1. Stock is properly validated before order creation
        2. Stock is atomically decremented
        3. No overselling occurs even under high concurrency
        
        Uses PostgreSQL's SELECT FOR UPDATE for row-level locking.
        
        Args:
            db: Database session
            order_data: Order creation data with items
            
        Returns:
            Created order instance with items
            
        Raises:
            ProductNotFoundError: If any product doesn't exist
            InsufficientStockError: If stock is insufficient for any item
        """
        # Extract product IDs and aggregate quantities (in case same product appears multiple times)
        product_quantities: Dict[int, int] = {}
        for item in order_data.items:
            if item.product_id in product_quantities:
                product_quantities[item.product_id] += item.quantity
            else:
                product_quantities[item.product_id] = item.quantity
        
        product_ids = list(product_quantities.keys())
        
        # Lock products with FOR UPDATE to prevent concurrent modifications
        # This is critical for preventing race conditions and overselling
        stmt = (
            select(Product)
            .where(Product.id.in_(product_ids))
            .with_for_update()  # Row-level locking
        )
        
        result = await db.execute(stmt)
        products = {p.id: p for p in result.scalars().all()}
        
        # Validate all products exist
        for product_id in product_ids:
            if product_id not in products:
                raise ProductNotFoundError(product_id)
        
        # Validate stock availability for ALL items before any modification
        # This ensures atomic all-or-nothing behavior
        for product_id, quantity in product_quantities.items():
            product = products[product_id]
            if product.stock_quantity < quantity:
                raise InsufficientStockError(
                    product_id,
                    product.stock_quantity,
                    quantity
                )
        
        # Create the order
        order = Order(status=OrderStatus.PENDING.value)
        db.add(order)
        await db.flush()  # Get order ID before creating items
        
        # Create order items and reduce stock
        for item in order_data.items:
            product = products[item.product_id]
            
            # Reduce stock
            product.stock_quantity -= item.quantity
            
            # Create order item with price captured at order time
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_order=product.price,
            )
            db.add(order_item)
        
        await db.commit()
        await db.refresh(order)  # Refresh to load items relationship
        
        return order
    
    @staticmethod
    async def get_order(db: AsyncSession, order_id: int) -> Order:
        """
        Get an order by ID with its items.
        
        Args:
            db: Database session
            order_id: Order ID
            
        Returns:
            Order instance with items
            
        Raises:
            OrderNotFoundError: If order doesn't exist
        """
        stmt = (
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items))
        )
        result = await db.execute(stmt)
        order = result.scalar_one_or_none()
        
        if not order:
            raise OrderNotFoundError(order_id)
        
        return order
    
    @staticmethod
    async def update_order_status(
        db: AsyncSession,
        order_id: int,
        new_status: OrderStatus
    ) -> Order:
        """
        Update an order's status with transition validation.
        
        Validates that the status transition is allowed according to
        the state machine defined in VALID_TRANSITIONS.
        
        Args:
            db: Database session
            order_id: Order ID
            new_status: New status to set
            
        Returns:
            Updated order instance
            
        Raises:
            OrderNotFoundError: If order doesn't exist
            InvalidStatusTransitionError: If transition is not allowed
        """
        order = await db.get(Order, order_id)
        
        if not order:
            raise OrderNotFoundError(order_id)
        
        # Get current status as enum
        try:
            current_status = OrderStatus(order.status)
        except ValueError:
            current_status = OrderStatus.PENDING
        
        # Validate status transition
        allowed_transitions = VALID_TRANSITIONS.get(current_status, set())
        if new_status not in allowed_transitions:
            raise InvalidStatusTransitionError(
                order.status,
                new_status.value
            )
        
        order.status = new_status.value
        await db.commit()
        await db.refresh(order)
        
        return order
