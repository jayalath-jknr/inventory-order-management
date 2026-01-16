"""Product service for business logic."""
from typing import List, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.schemas.product import ProductCreate


class ProductService:
    """Service class for product-related operations."""
    
    @staticmethod
    async def create_product(db: AsyncSession, product_data: ProductCreate) -> Product:
        """
        Create a new product.
        
        Args:
            db: Database session
            product_data: Product creation data
            
        Returns:
            Created product instance
        """
        product = Product(
            name=product_data.name,
            price=product_data.price,
            stock_quantity=product_data.stock_quantity,
        )
        db.add(product)
        await db.commit()
        await db.refresh(product)
        return product
    
    @staticmethod
    async def get_products(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 10
    ) -> Tuple[List[Product], int]:
        """
        Get paginated list of products.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (list of products, total count)
        """
        # Get total count
        count_stmt = select(func.count()).select_from(Product)
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0
        
        # Get paginated products
        stmt = select(Product).offset(skip).limit(limit).order_by(Product.id)
        result = await db.execute(stmt)
        products = list(result.scalars().all())
        
        return products, total
    
    @staticmethod
    async def get_product_by_id(db: AsyncSession, product_id: int) -> Product | None:
        """
        Get a product by its ID.
        
        Args:
            db: Database session
            product_id: Product ID
            
        Returns:
            Product instance or None if not found
        """
        return await db.get(Product, product_id)
