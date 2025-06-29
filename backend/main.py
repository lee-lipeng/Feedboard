import uuid
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from arq import create_pool
from arq.connections import RedisSettings
from fastapi.exceptions import RequestValidationError, HTTPException
from loguru import logger

from core.config import settings
from api import api_router
from db.init_db import init_db
from core.exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from core.logging_config import setup_logging

# 在应用启动的最开始就配置好日志
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理，在应用启动时初始化资源，在关闭时释放资源。
    """
    logger.info("Application startup...")
    await init_db()
    
    logger.info("Creating arq redis pool...")
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


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan,
    exception_handlers={
        HTTPException: http_exception_handler,
        RequestValidationError: validation_exception_handler,
        Exception: generic_exception_handler,
    }
)


# HTTP请求日志中间件
@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    """
    一个高效的日志中间件，使用Loguru记录每个请求的详细信息。
    为每个请求分配一个唯一的ID，方便追踪。
    """
    request_id = str(uuid.uuid4())
    # 将request_id绑定到日志上下文，后续的日志都会自动带上这个ID
    with logger.contextualize(request_id=request_id):
        logger.info(f"Request started: {request.method} {request.url.path}")
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            logger.info(
                f"Request finished: {response.status_code} | "
                f"Process Time: {process_time:.4f}s"
            )
            return response
        except Exception:
            # 使用 logger.exception 可以自动记录异常堆栈信息
            logger.exception("Unhandled exception during request processing.")
            # 异常将由FastAPI注册的处理器处理，这里仅作记录
            raise


# 设置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# 注册路由
app.include_router(api_router)

# 注册数据库
register_tortoise(
    app,
    db_url=settings.DATABASE_URI,
    modules={"models": settings.DB_MODELS},
    generate_schemas=settings.GENERATE_SCHEMAS,
    add_exception_handlers=True,
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
