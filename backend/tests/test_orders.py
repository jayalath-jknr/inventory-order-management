"""Tests for Order API endpoints - Critical business logic tests."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_order_success(client: AsyncClient) -> None:
    """
    Test successful order creation.
    
    This test verifies:
    1. Order is created successfully
    2. Stock is properly decremented
    3. Order contains correct items with captured prices
    """
    # Create products
    product1_response = await client.post(
        "/products",
        json={"name": "Product A", "price": "25.00", "stock_quantity": 100},
    )
    product1_id = product1_response.json()["id"]
    
    product2_response = await client.post(
        "/products",
        json={"name": "Product B", "price": "15.50", "stock_quantity": 50},
    )
    product2_id = product2_response.json()["id"]
    
    # Create order
    order_response = await client.post(
        "/orders",
        json={
            "items": [
                {"product_id": product1_id, "quantity": 10},
                {"product_id": product2_id, "quantity": 5},
            ]
        },
    )
    
    assert order_response.status_code == 201
    order_data = order_response.json()
    
    # Verify order structure
    assert order_data["status"] == "pending"
    assert len(order_data["items"]) == 2
    assert "created_at" in order_data
    
    # Verify stock was decremented
    products_response = await client.get("/products")
    products = {p["id"]: p for p in products_response.json()["items"]}
    
    assert products[product1_id]["stock_quantity"] == 90  # 100 - 10
    assert products[product2_id]["stock_quantity"] == 45  # 50 - 5


@pytest.mark.asyncio
async def test_create_order_insufficient_stock(client: AsyncClient) -> None:
    """
    Test order creation with insufficient stock.
    
    This test verifies:
    1. Order is rejected with 400 status
    2. Stock remains unchanged
    3. Error message is informative
    """
    # Create product with limited stock
    product_response = await client.post(
        "/products",
        json={"name": "Limited Product", "price": "50.00", "stock_quantity": 5},
    )
    product_id = product_response.json()["id"]
    
    # Attempt to order more than available
    order_response = await client.post(
        "/orders",
        json={
            "items": [
                {"product_id": product_id, "quantity": 10},  # Requesting 10, only 5 available
            ]
        },
    )
    
    assert order_response.status_code == 400
    error = order_response.json()
    assert "Insufficient stock" in error["detail"]
    
    # Verify stock was NOT changed
    products_response = await client.get("/products")
    products = {p["id"]: p for p in products_response.json()["items"]}
    assert products[product_id]["stock_quantity"] == 5  # Unchanged


@pytest.mark.asyncio
async def test_create_order_partial_insufficient_stock(client: AsyncClient) -> None:
    """
    Test order creation where one item has insufficient stock.
    
    This test verifies atomic behavior - if ANY item fails stock check,
    the entire order is rejected and NO stock is modified.
    """
    # Create products
    product1_response = await client.post(
        "/products",
        json={"name": "Product A", "price": "25.00", "stock_quantity": 100},
    )
    product1_id = product1_response.json()["id"]
    
    product2_response = await client.post(
        "/products",
        json={"name": "Product B", "price": "15.50", "stock_quantity": 3},  # Limited stock
    )
    product2_id = product2_response.json()["id"]
    
    # Attempt to create order - Product A has enough, Product B doesn't
    order_response = await client.post(
        "/orders",
        json={
            "items": [
                {"product_id": product1_id, "quantity": 10},  # OK
                {"product_id": product2_id, "quantity": 5},   # NOT OK - only 3 available
            ]
        },
    )
    
    assert order_response.status_code == 400
    
    # Verify NEITHER product's stock was changed (atomic rollback)
    products_response = await client.get("/products")
    products = {p["id"]: p for p in products_response.json()["items"]}
    
    assert products[product1_id]["stock_quantity"] == 100  # Unchanged
    assert products[product2_id]["stock_quantity"] == 3    # Unchanged


@pytest.mark.asyncio
async def test_create_order_product_not_found(client: AsyncClient) -> None:
    """Test order creation with non-existent product."""
    order_response = await client.post(
        "/orders",
        json={
            "items": [
                {"product_id": 99999, "quantity": 1},
            ]
        },
    )
    
    assert order_response.status_code == 404
    assert "not found" in order_response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_order_details(client: AsyncClient) -> None:
    """Test retrieving order details."""
    # Create product and order
    product_response = await client.post(
        "/products",
        json={"name": "Test Product", "price": "30.00", "stock_quantity": 50},
    )
    product_id = product_response.json()["id"]
    
    order_response = await client.post(
        "/orders",
        json={"items": [{"product_id": product_id, "quantity": 3}]},
    )
    order_id = order_response.json()["id"]
    
    # Get order details
    get_response = await client.get(f"/orders/{order_id}")
    
    assert get_response.status_code == 200
    order = get_response.json()
    assert order["id"] == order_id
    assert order["status"] == "pending"
    assert len(order["items"]) == 1
    assert order["items"][0]["quantity"] == 3
    assert order["items"][0]["price_at_order"] == "30.00"


@pytest.mark.asyncio
async def test_get_order_not_found(client: AsyncClient) -> None:
    """Test retrieving non-existent order."""
    response = await client.get("/orders/99999")
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_order_status_valid_transition(client: AsyncClient) -> None:
    """Test valid order status transition (pending -> shipped)."""
    # Create product and order
    product_response = await client.post(
        "/products",
        json={"name": "Test Product", "price": "20.00", "stock_quantity": 10},
    )
    product_id = product_response.json()["id"]
    
    order_response = await client.post(
        "/orders",
        json={"items": [{"product_id": product_id, "quantity": 1}]},
    )
    order_id = order_response.json()["id"]
    
    # Update status to shipped
    update_response = await client.patch(
        f"/orders/{order_id}/status",
        json={"status": "shipped"},
    )
    
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "shipped"


@pytest.mark.asyncio
async def test_update_order_status_invalid_transition(client: AsyncClient) -> None:
    """Test invalid order status transition (shipped -> pending)."""
    # Create product and order
    product_response = await client.post(
        "/products",
        json={"name": "Test Product", "price": "20.00", "stock_quantity": 10},
    )
    product_id = product_response.json()["id"]
    
    order_response = await client.post(
        "/orders",
        json={"items": [{"product_id": product_id, "quantity": 1}]},
    )
    order_id = order_response.json()["id"]
    
    # Ship the order
    await client.patch(f"/orders/{order_id}/status", json={"status": "shipped"})
    
    # Attempt to transition back to pending (invalid)
    update_response = await client.patch(
        f"/orders/{order_id}/status",
        json={"status": "pending"},
    )
    
    assert update_response.status_code == 400
    assert "Cannot transition" in update_response.json()["detail"]


@pytest.mark.asyncio
async def test_update_cancelled_order_status(client: AsyncClient) -> None:
    """Test that cancelled orders cannot be modified."""
    # Create product and order
    product_response = await client.post(
        "/products",
        json={"name": "Test Product", "price": "20.00", "stock_quantity": 10},
    )
    product_id = product_response.json()["id"]
    
    order_response = await client.post(
        "/orders",
        json={"items": [{"product_id": product_id, "quantity": 1}]},
    )
    order_id = order_response.json()["id"]
    
    # Cancel the order
    await client.patch(f"/orders/{order_id}/status", json={"status": "cancelled"})
    
    # Attempt to ship a cancelled order (invalid)
    update_response = await client.patch(
        f"/orders/{order_id}/status",
        json={"status": "shipped"},
    )
    
    assert update_response.status_code == 400
