import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


def _load_env_file() -> None:
    env_path = Path(__file__).resolve().parents[2] / ".env"

    if not env_path.exists():
        return

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        os.environ.setdefault(key, value)


_load_env_file()


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_env: str
    database_driver: str
    database_host: str
    database_port: int
    database_user: str
    database_password: str
    database_name: str
    database_echo: bool
    jwt_secret_key: str
    jwt_expires_minutes: int
    master_otp: str
    first_admin_email: str
    first_admin_mobile: str
    first_admin_name: str
    first_admin_age: int

    @property
    def database_url(self) -> str:
        if database_url := os.getenv("DATABASE_URL"):
            return database_url

        return (
            f"{self.database_driver}://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )


def _get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.lower() in {"1", "true", "yes", "on"}


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME"),
        app_env=os.getenv("APP_ENV"),
        database_driver=os.getenv("DATABASE_DRIVER"),
        database_host=os.getenv("DATABASE_HOST"),
        database_port=int(os.getenv("DATABASE_PORT")),
        database_user=os.getenv("DATABASE_USER"),
        database_password=os.getenv("DATABASE_PASSWORD"),
        database_name=os.getenv("DATABASE_NAME"),
        database_echo=_get_bool("DATABASE_ECHO"),
        jwt_secret_key=os.getenv("JWT_SECRET_KEY"),
        jwt_expires_minutes=int(os.getenv("JWT_EXPIRES_MINUTES")),
        master_otp=os.getenv("MASTER_OTP"),
        first_admin_email=os.getenv("FIRST_ADMIN_EMAIL"),
        first_admin_mobile=os.getenv("FIRST_ADMIN_MOBILE"),
        first_admin_name=os.getenv("FIRST_ADMIN_NAME"),
        first_admin_age=int(os.getenv("FIRST_ADMIN_AGE")),
    )
