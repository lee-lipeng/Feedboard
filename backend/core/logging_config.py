import sys
from loguru import logger

def setup_logging():
    """
    配置Loguru日志记录器。
    
    该函数会移除所有默认的日志处理器，并添加一个格式化的新处理器，
    从而确保所有日志（包括来自第三方库的）都由Loguru统一处理和格式化。
    """
    logger.remove()
    
    # 添加一个新的、格式化的控制台输出处理器
    # 这个格式会显示时间、日志级别、模块路径、函数名、行号以及日志消息，
    # 并使用颜色以增强可读性。
    logger.add(
        sys.stderr,
        level="INFO",
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        colorize=True,
    )
    
    # 您也可以取消注释下面的代码块，以将日志同时写入到文件中
    # logger.add(
    #     "logs/app_{time}.log", 
    #     level="INFO",
    #     rotation="10 MB",  # 当日志文件达到10MB时进行轮转
    #     retention="10 days",  # 最多保留10天的日志文件
    #     enqueue=True,  # 异步写入，避免阻塞应用
    #     format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"
    # )
    
    logger.info("Loguru logging has been successfully configured.")

