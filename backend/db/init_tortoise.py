from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from core.config import settings


def init_db(app: FastAPI) -> None:
    """
    初始化数据库连接
    """
    register_tortoise(
        app,
        db_url=settings.DATABASE_URI,
        modules={"models": settings.DB_MODELS},
        generate_schemas=settings.GENERATE_SCHEMAS,
        add_exception_handlers=True,
    )
