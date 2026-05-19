import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


DEFAULT_ENV = {
    "APP_NAME": "BuyBazar Test API",
    "APP_ENV": "test",
    "DATABASE_DRIVER": "postgresql+asyncpg",
    "DATABASE_HOST": "localhost",
    "DATABASE_PORT": "5432",
    "DATABASE_USER": "postgres",
    "DATABASE_PASSWORD": "postgres",
    "DATABASE_NAME": "buybazar_test",
    "DATABASE_ECHO": "false",
    "JWT_SECRET_KEY": "test-secret-key",
    "JWT_EXPIRES_MINUTES": "30",
    "MASTER_OTP": "123456",
    "FIRST_ADMIN_EMAIL": "admin@example.com",
    "FIRST_ADMIN_MOBILE": "9999999999",
    "FIRST_ADMIN_NAME": "Test Admin",
    "FIRST_ADMIN_AGE": "30",
}


for key, value in DEFAULT_ENV.items():
    os.environ.setdefault(key, value)
