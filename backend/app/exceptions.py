"""Custom exception classes for the application."""
from fastapi import HTTPException, status


class ProductNotFoundError(HTTPException):
    """Raised when a product is not found."""
    
    def __init__(self, product_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found"
        )


class OrderNotFoundError(HTTPException):
    """Raised when an order is not found."""
    
    def __init__(self, order_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with ID {order_id} not found"
        )


class InsufficientStockError(HTTPException):
    """Raised when there is not enough stock for an order."""
    
    def __init__(self, product_id: int, available: int, requested: int):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock for product {product_id}. Available: {available}, Requested: {requested}"
        )


class InvalidStatusTransitionError(HTTPException):
    """Raised when an invalid order status transition is attempted."""
    
    def __init__(self, current_status: str, new_status: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition order from '{current_status}' to '{new_status}'"
        )


class EmptyOrderError(HTTPException):
    """Raised when trying to create an order with no items."""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must contain at least one item"
        )
