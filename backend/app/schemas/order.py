"""Pydantic schemas for Order endpoints."""
from datetime import datetime
from decimal import Decimal
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import OrderStatus


class OrderItemCreate(BaseModel):
    """Schema for creating an order item."""
    
    product_id: int = Field(..., gt=0, description="ID of the product to order")
    quantity: int = Field(..., gt=0, description="Quantity to order (must be positive)")


class OrderItemResponse(BaseModel):
    """Schema for order item response."""
    
    id: int
    product_id: int
    quantity: int
    price_at_order: Decimal
    
    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    """Schema for creating a new order."""
    
    items: List[OrderItemCreate] = Field(
        ...,
        min_length=1,
        description="List of items to include in the order"
    )


class OrderResponse(BaseModel):
    """Schema for order response."""
    
    id: int
    created_at: datetime
    status: OrderStatus
    items: List[OrderItemResponse]
    
    model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status."""
    
    status: OrderStatus = Field(..., description="New status for the order")
