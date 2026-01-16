"""Product API endpoints."""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.schemas.product import ProductCreate, ProductListResponse, ProductResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Products"])
settings = get_settings()


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
    description="Add a new product with initial stock to the inventory.",
)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
) -> ProductResponse:
    """
    Create a new product.
    
    - **name**: Product name (1-255 characters)
    - **price**: Product price (must be positive)
    - **stock_quantity**: Initial stock quantity (must be non-negative)
    """
    product = await ProductService.create_product(db, product_data)
    return ProductResponse.model_validate(product)


@router.get(
    "",
    response_model=ProductListResponse,
    summary="List all products",
    description="Retrieve a paginated list of all products in the inventory.",
)
async def list_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        default=settings.DEFAULT_PAGE_SIZE,
        ge=1,
        le=settings.MAX_PAGE_SIZE,
        description="Maximum number of records to return",
    ),
    db: AsyncSession = Depends(get_db),
) -> ProductListResponse:
    """
    List products with pagination.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 10, max: 100)
    """
    products, total = await ProductService.get_products(db, skip=skip, limit=limit)
    return ProductListResponse(
        items=[ProductResponse.model_validate(p) for p in products],
        total=total,
        skip=skip,
        limit=limit,
    )
