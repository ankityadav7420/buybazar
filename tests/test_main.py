import asyncio

from app.main import app, root


def test_root_returns_api_status():
    response = asyncio.run(root())

    assert response == {"message": "API is running"}


def test_app_uses_configured_title():
    assert app.title == "BuyBazar Test API"
