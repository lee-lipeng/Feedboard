from fastapi import Request, status, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from loguru import logger


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    处理 FastAPI 的 HTTP 异常。
    这些是可预见的、由代码主动抛出的业务逻辑错误。
    """
    logger.warning(
        f"HTTP Exception caught: {exc.status_code} {exc.detail} "
        f"for request {request.method} {request.url.path}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    处理 Pydantic 数据验证失败的异常。
    当请求体、查询参数或路径参数的类型或格式不正确时触发。
    """
    # 记录详细的验证错误信息，方便后端调试
    logger.warning(
        f"请求参数验证失败 {request.method} {request.url.path}: {exc.errors()}"
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "请求参数验证失败", "errors": exc.errors()},
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """
    通用的服务器内部异常处理器。
    捕获所有未被其他处理器捕获的未知异常。
    """
    # 使用 logger.exception 可以自动捕获并记录完整的异常堆栈信息
    logger.exception(
        f"服务器异常 "
        f"{request.method} {request.url.path}"
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "服务器异常", "details": str(exc) if str(exc) else None,},
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """
    设置异常处理器

    为FastAPI应用添加全局异常处理器。

    Args:
        app: FastAPI应用实例
    """
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    logger.info("异常处理器设置完成")
