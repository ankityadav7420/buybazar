import asyncio
from dataclasses import dataclass
from uuid import uuid4

import pytest
from fastapi import HTTPException, status
from pydantic import ValidationError

from app.controllers import product_controller
from app.routers import product_router
from app.schemas.product_schemas import ProductBulkCreate, ProductCreate, ProductUpdate


@dataclass
class ProductStub:
    id: object
    name: str
    description: str = "A useful product"
    price: float = 100.0
    stock_quantity: int = 10
    is_deleted: int = 0


def test_bulk_product_payload_requires_at_least_one_product():
    with pytest.raises(ValidationError):
        ProductBulkCreate(products=[])


def test_create_products_bulk_returns_standard_message(monkeypatch):
    products = [
        ProductStub(id=uuid4(), name="Keyboard"),
        ProductStub(id=uuid4(), name="Mouse", price=50.0),
    ]

    async def fake_create_products_bulk(db, payloads):
        assert len(payloads) == 2
        return products

    monkeypatch.setattr(
        product_router.product_controller,
        "create_products_bulk",
        fake_create_products_bulk,
    )

    payload = ProductBulkCreate(
        products=[
            ProductCreate(
                name="Keyboard",
                description="Mechanical keyboard",
                price=100.0,
                stock_quantity=10,
            ),
            ProductCreate(
                name="Mouse",
                description="Wireless mouse",
                price=50.0,
                stock_quantity=20,
            ),
        ]
    )

    response = asyncio.run(
        product_router.create_products_bulk(payload=payload, db=object(), current_user={})
    )

    assert response == {
        "message": "Products created successfully",
        "data": products,
    }


def test_search_products_rejects_invalid_price_range():
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            product_controller.search_products(
                db=object(),
                min_price=500.0,
                max_price=100.0,
            )
        )

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "min_price cannot be greater than max_price"


def test_update_product_route_delegates_to_controller(monkeypatch):
    product = ProductStub(id=uuid4(), name="Updated Product", stock_quantity=5)

    async def fake_update_product(db, product_id, payload):
        assert product_id == product.id
        assert payload.stock_quantity == 5
        return product

    monkeypatch.setattr(product_router.product_controller, "update_product", fake_update_product)

    response = asyncio.run(
        product_router.update_product(
            product_id=product.id,
            payload=ProductUpdate(stock_quantity=5),
            db=object(),
            current_user={},
        )
    )

    assert response == product


def test_update_product_stock_route_delegates_to_controller(monkeypatch):
    product = ProductStub(id=uuid4(), name="Stocked Product", stock_quantity=25)

    async def fake_update_product_stock(db, product_id, stock_quantity):
        assert product_id == product.id
        assert stock_quantity == 25
        return product

    monkeypatch.setattr(
        product_router.product_controller,
        "update_product_stock",
        fake_update_product_stock,
    )

    response = asyncio.run(
        product_router.update_product_stock(
            product_id=product.id,
            payload=product_router.ProductStockUpdate(stock_quantity=25),
            db=object(),
            current_user={},
        )
    )

    assert response == product
