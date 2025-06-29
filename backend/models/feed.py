from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from .article import Article


class FeedCategory(str, Enum):
    NEWS = "news"
    TECH = "tech"
    DESIGN = "design"
    BUSINESS = "business"
    ENTERTAINMENT = "entertainment"
    SPORTS = "sports"
    SCIENCE = "science"
    HEALTH = "health"
    BLOG = "blog"
    OTHER = "other"


class Feed(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255, null=True)
    url = fields.CharField(max_length=512, unique=True)
    description = fields.TextField(null=True)
    website_url = fields.CharField(max_length=512, null=True)
    image_url = fields.CharField(max_length=512, null=True)
    category = fields.CharEnumField(FeedCategory, default=FeedCategory.OTHER)
    last_fetched = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # 通过中间表与用户建立多对多关系
    users = fields.ManyToManyField("models.User", related_name="subscribed_feeds", through="UserFeed")
    articles: fields.ReverseRelation["Article"]

    class Meta:
        table = "feeds"

    def __str__(self):
        return self.title


class UserFeed(models.Model):
    """用户订阅表 - 存储用户与Feed的订阅关系及个性化设置"""
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="feed_subscriptions")
    feed = fields.ForeignKeyField("models.Feed", related_name="user_subscriptions")
    title_override = fields.CharField(max_length=255, null=True)  # 用户可自定义标题
    category = fields.CharEnumField(FeedCategory, default=FeedCategory.OTHER)  # 用户自定义分类
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "user_feeds"
        unique_together = (("user", "feed"),)  # 确保用户不会重复订阅同一个源

    def __str__(self):
        return f"{self.user.email} - {self.feed.title}"


# 创建Pydantic模型
Feed_Pydantic = pydantic_model_creator(
    Feed, name="Feed"
)
FeedCreate_Pydantic = pydantic_model_creator(
    Feed, name="FeedCreate", exclude=("id", "created_at", "updated_at", "last_fetched")
)

# 用户订阅Pydantic模型
UserFeed_Pydantic = pydantic_model_creator(
    UserFeed, name="UserFeed"
)
UserFeedCreate_Pydantic = pydantic_model_creator(
    UserFeed, name="UserFeedCreate", exclude=("id", "created_at", "updated_at")
)


# 创建统一的API响应模型
class FeedResponse(BaseModel):
    """统一的Feed响应模型，前后端字段保持一致"""
    feed_id: int
    feed_title: str
    feed_url: str
    feed_description: Optional[str] = None
    feed_website_url: Optional[str] = None
    feed_image_url: Optional[str] = None
    feed_last_fetched: Optional[datetime] = None
    feed_category: FeedCategory = FeedCategory.OTHER
    feed_created_at: datetime
    feed_updated_at: datetime


class UserFeedResponse(BaseModel):
    """统一的UserFeed响应模型，包含用户特定信息"""
    id: int
    title_override: Optional[str] = None
    category: FeedCategory
    created_at: datetime
    updated_at: datetime
    feed_id: int
    feed_title: str
    feed_url: str
    feed_description: Optional[str] = None
    feed_website_url: Optional[str] = None
    feed_image_url: Optional[str] = None
    feed_last_fetched: Optional[datetime] = None
