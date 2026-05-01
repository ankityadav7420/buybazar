from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection


async def sync_schema(conn: AsyncConnection) -> None:
    await conn.execute(
        text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_deleted INTEGER DEFAULT 0")
    )
    await conn.execute(
        text("UPDATE users SET is_deleted = 0 WHERE is_deleted IS NULL")
    )
    await conn.execute(
        text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR DEFAULT 'user'")
    )
    await conn.execute(
        text("UPDATE users SET role = 'user' WHERE role IS NULL")
    )
    await conn.execute(
        text("ALTER TABLE products ADD COLUMN IF NOT EXISTS is_deleted INTEGER DEFAULT 0")
    )
    await conn.execute(
        text("ALTER TABLE products ADD COLUMN IF NOT EXISTS stock_quantity INTEGER DEFAULT 0")
    )
    await conn.execute(
        text("UPDATE products SET is_deleted = 0 WHERE is_deleted IS NULL")
    )
    await conn.execute(
        text("UPDATE products SET stock_quantity = 0 WHERE stock_quantity IS NULL")
    )
