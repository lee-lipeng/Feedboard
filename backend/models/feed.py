from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from enum import Enum

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
    id = fields.IntField(pk=True, description="订阅源唯一ID")
    title = fields.CharField(max_length=255, null=True, description="订阅源标题")
    url = fields.CharField(max_length=512, unique=True, description="订阅源链接")
    description = fields.TextField(null=True, description="订阅源描述")
    website_url = fields.CharField(max_length=512, null=True, description="订阅源官网链接")
    image_url = fields.CharField(max_length=512, null=True, description="订阅源图片链接")
    category = fields.CharEnumField(FeedCategory, default=FeedCategory.OTHER, description="订阅源分类")
    last_fetched = fields.DatetimeField(null=True, description="最后更新时间")
    created_at = fields.DatetimeField(auto_now_add=True, description="记录创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="记录更新时间")

    # 通过中间表与用户建立多对多关系
    users = fields.ManyToManyField("models.User", related_name="subscribed_feeds", through="UserFeed")
    articles: fields.ReverseRelation["Article"]

    class Meta:
        table = "feeds"

    def __str__(self):
        return self.title


class UserFeed(models.Model):
    """用户订阅表 - 存储用户与Feed的订阅关系及个性化设置"""
    id = fields.IntField(pk=True, description="用户订阅ID")
    user = fields.ForeignKeyField("models.User", related_name="feed_subscriptions", on_delete=fields.CASCADE, description="关联的用户")
    feed = fields.ForeignKeyField("models.Feed", related_name="user_subscriptions", on_delete=fields.CASCADE, description="关联的订阅源")
    title_override = fields.CharField(max_length=255, null=True, description="用户自定义标题")
    category = fields.CharEnumField(FeedCategory, default=FeedCategory.OTHER, description="用户自定义分类")
    created_at = fields.DatetimeField(auto_now_add=True, description="记录创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="记录更新时间")

    class Meta:
        table = "user_feeds"
        unique_together = (("user", "feed"),)  # 确保用户不会重复订阅同一个源

    def __str__(self):
        return f"{self.user.email} - {self.feed.title}"
