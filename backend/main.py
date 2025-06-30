from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from arq import create_pool
from arq.connections import RedisSettings
from loguru import logger
from tortoise.contrib.fastapi import register_tortoise

from core.config import settings
from db.init_db import init_db, TORTOISE_ORM
from core.exception_handlers import setup_exception_handlers
from core.logging_config import setup_logging
from api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理，在应用启动时初始化资源，在关闭时释放资源。
    """
    logger.info("Application startup...")

    await init_db()

    app.state.arq_pool = await create_pool(
        RedisSettings(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD or None,
            database=settings.REDIS_DB
        )
    )
    yield
    logger.info("Application shutdown...")
    await app.state.arq_pool.close()


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.PROJECT_VERSION,
        lifespan=lifespan
    )

    # 设置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition"],
    )

    # 注册 Tortoise-ORM
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=False,
        add_exception_handlers=True,
    )

    # 设置异常处理器
    setup_exception_handlers(app)

    # 注册路由
    app.include_router(api_router)

    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:create_app", host="0.0.0.0", port=8000, reload=True, factory=True)
