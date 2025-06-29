import os
import secrets
from typing import List, Dict, Any

from dotenv import load_dotenv, set_key
from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings

# 加载 .env 文件
load_dotenv()

# 检查环境变量中是否已存在 SECRET_KEY
if not os.getenv("SECRET_KEY"):
    # 如果不存在，生成一个新的密钥
    new_secret_key = secrets.token_urlsafe(32)
    # 将密钥写入 .env 文件
    set_key(".env", "SECRET_KEY", new_secret_key)
    # 将生成的密钥添加到环境变量中
    os.environ["SECRET_KEY"] = new_secret_key


class Settings(BaseSettings):
    # 应用配置
    PROJECT_NAME: str = "Feedboard API"
    PROJECT_DESCRIPTION: str = "RSS 阅读器服务 API"
    PROJECT_VERSION: str = "0.1.0"

    # 安全配置
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    ALGORITHM: str = "HS256"

    # CORS配置
    CORS_ORIGINS: List[str] = [
    "http://localhost",
    "http://localhost:5173",  # Vue 开发服务器默认端口
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

    # 数据库配置
    # 数据库类型: "postgres" 或 "sqlite"
    DB_TYPE: str = os.getenv("DB_TYPE", "sqlite")

    # PostgreSQL配置
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "123456")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "feedboard")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))

    # SQLite配置
    SQLITE_DB_FILE: str = os.getenv("SQLITE_DB_FILE", "feedboard.db")

    # 数据库URI
    DATABASE_URI: str = ""

    @field_validator("DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str, values: Dict[str, Any]) -> Any:
        if isinstance(v, str) and v != "":
            return v

        if values.data.get("DB_TYPE") == "sqlite":
            db_file = values.data.get("SQLITE_DB_FILE")
            return f"sqlite://./{db_file}"
        else:
            return PostgresDsn.build(
                scheme="postgres",
                username=values.data.get("POSTGRES_USER"),
                password=values.data.get("POSTGRES_PASSWORD"),
                host=values.data.get("POSTGRES_SERVER"),
                port=values.data.get("POSTGRES_PORT"),
                path=f"/{values.data.get('POSTGRES_DB') or ''}",
            ).unicode_string()

    # Redis配置
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")

    # ORM配置
    DB_MODELS: List[str] = ["models.user", "models.feed", "models.article"]
    GENERATE_SCHEMAS: bool = True

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
