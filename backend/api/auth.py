from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from loguru import logger

from models.user import User_Pydantic
from core.security import create_access_token
from core.config import settings
from services.user_service import authenticate_user, create_user, get_user_by_email

router = APIRouter()


class Token(BaseModel):
    """JWT 令牌响应模型"""
    access_token: str
    token_type: str


class UserRegister(BaseModel):
    """用户注册请求体"""
    email: EmailStr
    password: str


@router.post("/login", response_model=Token, summary="用户登录获取令牌")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    """
    使用 OAuth2 标准的密码流进行用户认证，成功后返回 JWT。
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        logger.warning(f"用户 {form_data.username} 登录失败, 邮箱或密码不正确.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(subject=user.id, expires_delta=access_token_expires)

    logger.success(f"用户 [{user.email}] 登录成功.")
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=User_Pydantic, status_code=status.HTTP_201_CREATED, summary="注册新用户")
async def register_user(user_in: UserRegister) -> User_Pydantic:
    """
    创建新用户。
    在创建前会检查邮箱是否已被占用。
    """
    existing_user = await get_user_by_email(user_in.email)
    if existing_user:
        logger.warning(f"注册失败：电子邮件 {user_in.email} 已存在.")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该邮箱地址已被注册"
        )

    user = await create_user(email=user_in.email, password=user_in.password)
    logger.success(f"用户 [{user.email}] 注册成功.")

    return await User_Pydantic.from_tortoise_orm(user)
