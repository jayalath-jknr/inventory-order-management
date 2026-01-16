"""Pydantic schemas for Product endpoints."""
from decimal import Decimal
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    """Schema for creating a new product."""
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the product"
    )
    price: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        description="Price of the product (must be positive)"
    )
    stock_quantity: int = Field(
        ...,
        ge=0,
        description="Initial stock quantity (must be non-negative)"
    )


class ProductResponse(BaseModel):
    """Schema for product response."""
    
    id: int
    name: str
    price: Decimal
    stock_quantity: int
    
    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    """Schema for paginated product list response."""
    
    items: List[ProductResponse]
    total: int
    skip: int
    limit: int
