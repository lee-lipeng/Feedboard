from datetime import datetime, timedelta
from typing import Any, Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from loguru import logger

from core.config import settings
from models.user import User

# OAuth2 密码流的 tokenUrl 指向登录接口
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# 使用 bcrypt 算法进行密码哈希
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    根据给定的主题（通常是用户ID）和过期时间创建一个新的JWT访问令牌。
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码是否与哈希密码匹配。"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """对明文密码进行哈希处理。"""
    return pwd_context.hash(password)


async def get_current_user_from_token(token: str) -> Optional[User]:
    """
    从JWT令牌中解析并获取用户，认证失败时返回None。
    此函数专为WebSocket等不适合直接抛出HTTPException的场景设计。
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            logger.warning("令牌解码失败：缺少 'sub' 声明。")
            return None
    except JWTError as e:
        logger.warning(f"令牌解码过程中发生JWT错误: {e}")
        return None

    user = await User.get_or_none(id=int(user_id))
    if user is None:
        logger.warning(f"认证失败：未找到令牌中ID为 {user_id} 的用户。")
        return None
    
    if not user.is_active:
        logger.warning(f"认证失败：用户 {user.email} 处于非活动状态。")
        return None
        
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    一个FastAPI依赖项，用于从请求中获取JWT，验证并返回当前用户。
    如果验证失败，会抛出相应的HTTPException。
    """
    user = await get_current_user_from_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无法验证您的凭据，请重新登录。",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_superuser(current_user: User = Depends(get_current_user)) -> User:
    """
    一个FastAPI依赖项，用于验证当前用户是否为超级用户。
    如果不是，则抛出403 Forbidden异常。
    """
    if not current_user.is_superuser:
        logger.warning(f"权限不足：非管理员用户 '{current_user.email}' 尝试访问管理员接口。")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="此操作需要管理员权限。")
    return current_user
