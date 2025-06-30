from typing import Optional
from loguru import logger

from models.user import User
from core.security import get_password_hash, verify_password


async def get_user_by_email(email: str) -> Optional[User]:
    """
    通过邮箱地址查找用户。
    """
    return await User.get_or_none(email=email)


async def create_user(email: str, password: str) -> User:
    """
    创建一个新用户并将其密码哈希后存入数据库。
    """
    hashed_password = get_password_hash(password)
    user = await User.create(
        email=email,
        hashed_password=hashed_password
    )
    logger.success(f"已成功创建用户 {email} ID {user.id}")
    return user


async def authenticate_user(email: str, password: str) -> Optional[User]:
    """
    验证用户的邮箱和密码是否匹配。
    如果用户不存在或密码错误，则返回 None。
    """
    user = await get_user_by_email(email)
    if not user:
        logger.warning(f"身份验证失败：找不到电子邮件为｛email｝的用户.")
        return None

    if not verify_password(password, user.hashed_password):
        logger.warning(f"身份验证失败：用户｛email｝的密码无效.")
        return None

    logger.info(f"用户｛email｝已成功通过身份验证.")
    return user
