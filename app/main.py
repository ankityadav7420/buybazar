from fastapi import FastAPI
from contextlib import asynccontextmanager

from .core.config import get_settings
from .core.database import engine, Base
from .core.schema import sync_schema
from .core.seed import seed_first_admin
from .models import (
    cart_models,
    order_items_models,
    order_models,
    payment_status_history_models,
    payments_models,
    product_models,
    user_models,
)
from .routers.cart_router import router as cart_router
from .routers.auth_router import router as auth_router
from .routers.order_route import router as order_router
from .routers.product_router import router as product_router
from .routers.user_router import router as user_router

settings = get_settings()


# -----------------------------
# Lifespan (modern production way)
# -----------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await sync_schema(conn)
        await seed_first_admin(conn)

    yield  # app runs here

    # Shutdown (optional cleanup)
    await engine.dispose()


# -----------------------------
# App instance (MUST be first)
# -----------------------------
app = FastAPI(title=settings.app_name, lifespan=lifespan)


# -----------------------------
# Routes
# -----------------------------
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(product_router)
app.include_router(cart_router)
app.include_router(order_router)


@app.get("/")
async def root():
    return {"message": "API is running.deployed to server"}
