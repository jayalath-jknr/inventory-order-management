"""Tests for Product API endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_product_success(client: AsyncClient) -> None:
    """Test successful product creation."""
    response = await client.post(
        "/products",
        json={
            "name": "Test Product",
            "price": "19.99",
            "stock_quantity": 100,
        },
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Product"
    assert data["price"] == "19.99"
    assert data["stock_quantity"] == 100
    assert "id" in data


@pytest.mark.asyncio
async def test_create_product_invalid_price(client: AsyncClient) -> None:
    """Test product creation with invalid price."""
    response = await client.post(
        "/products",
        json={
            "name": "Test Product",
            "price": "-10.00",
            "stock_quantity": 100,
        },
    )
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_create_product_negative_stock(client: AsyncClient) -> None:
    """Test product creation with negative stock."""
    response = await client.post(
        "/products",
        json={
            "name": "Test Product",
            "price": "19.99",
            "stock_quantity": -5,
        },
    )
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_list_products_empty(client: AsyncClient) -> None:
    """Test listing products when none exist."""
    response = await client.get("/products")
    
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_products_with_pagination(client: AsyncClient) -> None:
    """Test listing products with pagination."""
    # Create multiple products
    for i in range(15):
        await client.post(
            "/products",
            json={
                "name": f"Product {i}",
                "price": "10.00",
                "stock_quantity": 50,
            },
        )
    
    # Get first page
    response = await client.get("/products?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 10
    assert data["total"] == 15
    
    # Get second page
    response = await client.get("/products?skip=10&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 5
    assert data["total"] == 15
