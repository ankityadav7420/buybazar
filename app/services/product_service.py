from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.product_models import Product
from app.schemas.product_schemas import ProductCreate, ProductSortBy, ProductUpdate


# Create a product available for carts and checkout.
async def create_product(db: AsyncSession, product: ProductCreate):
    db_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock_quantity=product.stock_quantity
    )

    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


async def create_products_bulk(db: AsyncSession, products: list[ProductCreate]):
    db_products = [
        Product(
            name=product.name,
            description=product.description,
            price=product.price,
            stock_quantity=product.stock_quantity,
        )
        for product in products
    ]

    db.add_all(db_products)
    await db.commit()

    for product in db_products:
        await db.refresh(product)

    return db_products


# Return all product rows, including soft-deleted products.
async def get_all_products(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(Product).offset(skip).limit(limit)
    )
    return result.scalars().all()


# Return only products that users can buy.
async def get_active_products(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(Product).where(Product.is_deleted == 0).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def search_products(
    db: AsyncSession,
    q: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    in_stock: bool | None = None,
    active_only: bool = True,
    sort_by: ProductSortBy = "name_asc",
    skip: int = 0,
    limit: int = 100,
):
    query = select(Product)

    if active_only:
        query = query.where(Product.is_deleted == 0)

    if q:
        query = query.where(Product.name.ilike(f"%{q.strip()}%"))

    if min_price is not None:
        query = query.where(Product.price >= min_price)

    if max_price is not None:
        query = query.where(Product.price <= max_price)

    if in_stock is True:
        query = query.where(Product.stock_quantity > 0)
    elif in_stock is False:
        query = query.where(Product.stock_quantity == 0)

    sort_options = {
        "name_asc": Product.name.asc(),
        "name_desc": Product.name.desc(),
        "price_asc": Product.price.asc(),
        "price_desc": Product.price.desc(),
    }
    query = query.order_by(sort_options[sort_by]).offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


# Fetch one product by UUID.
async def get_product_by_id(db: AsyncSession, product_id: UUID):
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    return result.scalar_one_or_none()


async def update_product(db: AsyncSession, product_id: UUID, payload: ProductUpdate):
    product = await get_product_by_id(db, product_id)

    if product is None:
        return None

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(product, field, value)

    await db.commit()
    await db.refresh(product)
    return product


async def update_product_stock(db: AsyncSession, product_id: UUID, stock_quantity: int):
    product = await get_product_by_id(db, product_id)

    if product is None:
        return None

    product.stock_quantity = stock_quantity
    await db.commit()
    await db.refresh(product)
    return product


# Permanently remove a product row.
async def delete_product_by_id(db: AsyncSession, product_id: UUID):
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()

    if product:
        await db.delete(product)
        await db.commit()

    return product

# Soft delete a product so it no longer appears as active.
async def soft_delete_product_by_id(db: AsyncSession, product_id: UUID):
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()

    if product:
        product.is_deleted = 1
        await db.commit()

    return product
