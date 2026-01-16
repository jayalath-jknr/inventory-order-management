"""Order API endpoints."""
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order",
    description=(
        "Create a new order with the specified items. "
        "Stock is validated and atomically decremented. "
        "Uses row-level locking to prevent race conditions."
    ),
)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """
    Create a new order.
    
    - **items**: List of product IDs and quantities
    
    The endpoint will:
    1. Validate all products exist
    2. Check stock availability for all items
    3. Atomically reduce stock and create the order
    
    Returns 400 if any product has insufficient stock.
    Returns 404 if any product doesn't exist.
    """
    order = await OrderService.create_order(db, order_data)
    return OrderResponse.model_validate(order)


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get order details",
    description="Retrieve details of a specific order including all items.",
)
async def get_order(
    order_id: int = Path(..., gt=0, description="Order ID"),
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """
    Get order details by ID.
    
    Returns the order with all its items, including:
    - Order ID and status
    - Creation timestamp
    - List of items with quantities and prices at time of order
    """
    order = await OrderService.get_order(db, order_id)
    return OrderResponse.model_validate(order)


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
    summary="Update order status",
    description=(
        "Update the status of an order. "
        "Valid transitions: Pending → Shipped, Pending → Cancelled. "
        "Shipped and Cancelled are terminal states."
    ),
)
async def update_order_status(
    status_update: OrderStatusUpdate,
    order_id: int = Path(..., gt=0, description="Order ID"),
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """
    Update order status.
    
    - **status**: New status (pending, shipped, cancelled)
    
    Valid transitions:
    - pending → shipped
    - pending → cancelled
    
    Returns 400 if the transition is invalid.
    Returns 404 if the order doesn't exist.
    """
    order = await OrderService.update_order_status(db, order_id, status_update.status)
    return OrderResponse.model_validate(order)
