import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent
ENV_DIR = BASE_DIR / "environments"
env_style = os.getenv("ENV_TYPE", "dev")
env_file = ENV_DIR / f".env.{env_style}"

class DBSettings(BaseSettings):
    user: str
    password: str
    host: str = "localhost"
    port: int = 5432
    name: str

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    model_config = SettingsConfigDict(
        env_prefix="DB_",
        env_file=env_file
    )

