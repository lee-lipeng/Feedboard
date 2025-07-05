from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from loguru import logger

from models.user import User, User_Pydantic
from core.security import get_current_user, get_password_hash

router = APIRouter()


class UserUpdate(BaseModel):
    """用户更新请求体"""
    email: Optional[EmailStr] = None
    password: Optional[str] = None


@router.get("/me", response_model=User_Pydantic, summary="获取当前用户信息")
async def get_current_user_info(current_user: User = Depends(get_current_user)) -> User_Pydantic:
    """
    获取当前登录用户的详细信息。
    """
    logger.info(f"用户 [{current_user.email}] 获取个人资料")
    return await User_Pydantic.from_tortoise_orm(current_user)


@router.put("/me", response_model=User_Pydantic, summary="更新当前用户信息")
async def update_current_user_info(
        user_in: UserUpdate,
        current_user: User = Depends(get_current_user)
) -> User_Pydantic:
    """
    更新当前用户的邮箱或密码。
    """
    update_data = user_in.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="没有提供任何需要更新的信息"
        )

    # 更新邮箱
    if user_in.email and user_in.email != current_user.email:
        existing_user = await User.filter(email=user_in.email).first()
        if existing_user:
            logger.warning(
                f"用户 [{current_user.email}] 更新邮箱失败，邮箱 {user_in.email} 已被其他账户使用"
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="该邮箱地址已被其他账户使用"
            )
        current_user.email = user_in.email
        logger.success(f"用户 [{current_user.email}] 电子邮件已更新至 {user_in.email}")

    # 更新密码
    if user_in.password:
        hashed_password = get_password_hash(user_in.password)
        current_user.hashed_password = hashed_password
        logger.success(f"用户 [{current_user.email}] 密码已更新.")

    await current_user.save()
    return await User_Pydantic.from_tortoise_orm(current_user)


@router.delete("/me", summary="注销当前用户")
async def delete_current_user(current_user: User = Depends(get_current_user)):
    """
    注销当前用户。

    使用物理删除清除与用户相关的一切数据，包括用户的订阅，文章，偏好设置等。
    """
    await current_user.delete()
    logger.success(f"用户 [{current_user.email}] 已成功注销.")
    return {"message": "用户已成功注销"}
