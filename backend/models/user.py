from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator

from .feed import Feed


class User(models.Model):
    id = fields.IntField(pk=True, description="用户ID")
    email = fields.CharField(max_length=255, unique=True, description="邮箱")
    hashed_password = fields.CharField(max_length=255, description="密码的哈希值")
    is_active = fields.BooleanField(default=True, description="是否激活")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    # 用户偏好设置
    font_size = fields.IntField(default=100, description="字体大小")  # 百分比值，如 80%, 100%, 120%
    latest_articles_days = fields.IntField(default=7, description="最新文章天数")

    # 应用设置
    notifications_enabled = fields.BooleanField(default=True, description="是否启用通知")
    auto_refresh_enabled = fields.BooleanField(default=True, description="是否启用自动刷新")
    refresh_interval = fields.IntField(default=60, description="刷新间隔（分钟）")
    default_sorting = fields.CharField(max_length=20, default="newest", description="默认排序方式")  # 'newest', 'oldest', 'source'

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
