"""Enum definitions for the application."""
import enum


class OrderStatus(str, enum.Enum):
    """Status of an order."""
    
    PENDING = "pending"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"
