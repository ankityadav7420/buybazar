from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.user_models import User


def _seed_first_admin(sync_conn) -> None:
    settings = get_settings()

    if not settings.first_admin_email or not settings.first_admin_mobile:
        return

    session = Session(bind=sync_conn)
    existing_admin = session.execute(
        select(User).where(User.email == settings.first_admin_email.lower())
    ).scalars().first()

    if existing_admin:
        return

    session.add(
        User(
            name=settings.first_admin_name,
            email=settings.first_admin_email.lower(),
            mobile=settings.first_admin_mobile,
            age=settings.first_admin_age,
            role="admin",
        )
    )
    session.flush()


async def seed_first_admin(conn: AsyncConnection) -> None:
    await conn.run_sync(_seed_first_admin)
