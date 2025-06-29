import asyncio
import logging
import os

from tortoise import Tortoise

from  core.config import settings
from  services.user_service import get_user_by_email, create_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db() -> None:
    """
    初始化数据库
    """
    try:
        logger.info(f"初始化数据库连接: {settings.DATABASE_URI}")
        
        # 如果使用SQLite并且文件不存在，创建目录
        if settings.DB_TYPE == "sqlite":
            db_path = settings.SQLITE_DB_FILE
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
                logger.info(f"创建SQLite数据库目录: {db_dir}")
        
        # 初始化Tortoise ORM
        await Tortoise.init(
            db_url=settings.DATABASE_URI,
            modules={"models": settings.DB_MODELS}
        )
        
        # 生成数据库结构
        logger.info("生成数据库结构")
        await Tortoise.generate_schemas()
        
        # 创建初始超级用户
        await create_initial_superuser()
        
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise
    finally:
        # 关闭数据库连接
        await Tortoise.close_connections()

async def create_initial_superuser() -> None:
    """
    创建初始超级用户
    """
    try:
        # 检查是否已存在超级用户
        admin_email = "123@123.com"
        existing_admin = await get_user_by_email(admin_email)
        
        if not existing_admin:
            logger.info("创建初始超级用户")
            user = await create_user(
                email=admin_email,
                password="123"
            )
            
            # 设置为超级用户
            from  models.user import User
            admin = await User.get(id=user.id)
            admin.is_superuser = True
            await admin.save()
            logger.info(f"超级用户已创建: {admin.email}")
        else:
            logger.info("超级用户已存在，跳过创建")
    except Exception as e:
        logger.error(f"创建超级用户失败: {e}")
        raise

if __name__ == "__main__":
    """
    从命令行运行: python -m  db.init_db
    """
    try:
        asyncio.run(init_db())
    except KeyboardInterrupt:
        logger.info("用户中断操作")
    except Exception as e:
        logger.error(f"初始化过程中出错: {e}")
        raise 