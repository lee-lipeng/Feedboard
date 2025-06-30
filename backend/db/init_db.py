import os

from loguru import logger
from tortoise import Tortoise

from core.config import settings
from services.user_service import get_user_by_email, create_user

TORTOISE_ORM = {
    "connections": {"default": settings.DATABASE_URI},
    "apps": {
        "models": {
            "models": settings.DB_MODELS,
            "default_connection": "default",
        },
    },
}


async def init_db() -> None:
    """
    创建初始用户
    """
    try:
        # 如果使用SQLite并且文件不存在，创建目录
        if settings.DB_TYPE == "sqlite":
            db_path = settings.SQLITE_DB_FILE
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
                logger.info(f"创建SQLite数据库目录: {db_dir}")

        await Tortoise.init(config=TORTOISE_ORM)
        # 创建初始用户
        await create_initial_user()

        logger.info("数据库初始化流程完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise
    finally:
        await Tortoise.close_connections()


async def create_initial_user() -> None:
    """
    初始化用户
    """
    try:
        admin_email = "123@123.com"
        existing_admin = await get_user_by_email(admin_email)

        if not existing_admin:
            logger.info("创建初始用户...")
            user = await create_user(
                email=admin_email,
                password="123"
            )
            logger.info(f"用户已创建: {user.email}")
        else:
            logger.info("初始用户已存在，跳过创建。")
    except Exception as e:
        logger.error(f"创建初始用户失败: {e}")
        raise
