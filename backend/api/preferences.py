from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, model_validator, ConfigDict
from loguru import logger

from models.user import User
from core.security import get_current_user

router = APIRouter()


class UserPreferences(BaseModel):
    """用户偏好设置模型"""
    model_config = ConfigDict(from_attributes=True)

    font_size: Optional[int] = Field(None, ge=80, le=120, description="字体大小百分比 (80-120)")
    latest_articles_days: Optional[int] = Field(None, ge=1, le=30, description="'最新'视图显示天数 (1-30)")
    notifications_enabled: Optional[bool] = Field(None, description="是否启用新文章桌面通知")
    auto_refresh_enabled: Optional[bool] = Field(None, description="是否启用后台自动刷新")
    refresh_interval: Optional[int] = Field(None, description="自动刷新间隔（分钟）")
    default_sorting: Optional[str] = Field(None, description="文章列表默认排序方式")

    @model_validator(mode='before')
    @classmethod
    def validate_settings(cls, values):
        # 验证刷新频率，仅当值不为None时
        if 'refresh_interval' in values and values['refresh_interval'] is not None and values['refresh_interval'] not in [15, 30, 60, 360, 720, 1440]:
            raise ValueError("无效的刷新频率")
        # 验证排序方式，仅当值不为None时
        if 'default_sorting' in values and values['default_sorting'] is not None and values['default_sorting'] not in ['newest', 'oldest', 'source']:
            raise ValueError("无效的排序方式")
        return values


@router.get("", response_model=UserPreferences, summary="获取用户偏好设置")
async def get_user_preferences(current_user: User = Depends(get_current_user)) -> UserPreferences:
    """
    获取当前登录用户的偏好设置。
    """
    logger.debug(f"获取用户偏好 {current_user.email}")
    return UserPreferences.model_validate(current_user)


@router.put("", response_model=UserPreferences, summary="更新用户偏好设置")
async def update_user_preferences(
    preferences: UserPreferences,
    current_user: User = Depends(get_current_user)
) -> UserPreferences:
    """
    更新当前用户的偏好设置。
    只会更新请求体中提供的字段。
    """
    update_data = preferences.model_dump(exclude_unset=True)
    if not update_data:
        logger.warning(f"没有提供任何需要更新的偏好设置 {current_user.email}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="没有提供任何需要更新的偏好设置")

    for key, value in update_data.items():
        setattr(current_user, key, value)

    await current_user.save()
    logger.info(f"用户的偏好设置已成功更新 {current_user.email} 数据: {update_data}")

    return UserPreferences.model_validate(current_user)
