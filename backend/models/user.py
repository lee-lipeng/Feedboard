from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator

from .feed import Feed


class User(models.Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True)
    hashed_password = fields.CharField(max_length=255)
    is_active = fields.BooleanField(default=True)
    is_superuser = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    # 用户偏好设置
    font_size = fields.IntField(default=100)  # 百分比值，如 80%, 100%, 120%
    latest_articles_days = fields.IntField(default=7) # 最近文章显示天数

    # 新增的应用设置
    notifications_enabled = fields.BooleanField(default=True)
    auto_refresh_enabled = fields.BooleanField(default=True)
    refresh_interval = fields.IntField(default=60)  # 刷新频率（分钟）
    default_sorting = fields.CharField(max_length=20, default="newest") # 'newest', 'oldest', 'source'

    # 反向关系
    feeds: fields.ReverseRelation["Feed"]

    class Meta:
        table = "users"

    def __str__(self):
        return f"{self.email}"


# 创建Pydantic模型
User_Pydantic = pydantic_model_creator(
    User, name="User", exclude=("hashed_password",)
)
UserCreate_Pydantic = pydantic_model_creator(
    User, name="UserCreate", exclude_readonly=True
)
