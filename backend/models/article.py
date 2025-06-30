from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class Article(models.Model):
    """文章模型 - 代表一篇独立的新闻或博客文章。"""
    id = fields.IntField(pk=True, description="文章唯一ID")
    title = fields.CharField(max_length=255, description="文章标题")
    url = fields.CharField(max_length=512, unique=True, description="文章原始链接")
    author = fields.CharField(max_length=255, null=True, description="文章作者")
    summary = fields.TextField(null=True, description="文章摘要或简介")
    content = fields.TextField(null=True, description="文章完整内容（HTML格式）")
    image_url = fields.CharField(max_length=512, null=True, description="文章特色图片链接")
    published_at = fields.DatetimeField(null=True, index=True, description="文章发布时间")
    guid = fields.CharField(max_length=512, index=True, description="文章全局唯一标识符")
    created_at = fields.DatetimeField(auto_now_add=True, description="记录创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="记录更新时间")

    # 关系字段
    feed = fields.ForeignKeyField("models.Feed", related_name="articles", description="所属订阅源")
    users = fields.ManyToManyField("models.User", related_name="interacted_articles", through="UserArticle", description="与此文章有交互的用户")

    class Meta:
        table = "articles"
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title


class UserArticle(models.Model):
    """
    用户-文章关系模型 - 存储用户与特定文章的交互状态。
    这是一个多对多关系的中间表。
    """
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="article_interactions", description="关联的用户")
    article = fields.ForeignKeyField("models.Article", related_name="user_interactions", description="关联的文章")
    
    # 交互状态字段
    is_read = fields.BooleanField(default=False, index=True, description="是否已读")
    is_favorite = fields.BooleanField(default=False, index=True, description="是否收藏")
    read_later = fields.BooleanField(default=False, index=True, description="是否标记为稍后读")
    read_position = fields.IntField(default=0, description="阅读位置（例如滚动条百分比），用于继续阅读")
    
    created_at = fields.DatetimeField(auto_now_add=True, description="记录创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="记录更新时间")
    
    class Meta:
        table = "user_articles"
        unique_together = (("user", "article"),)  # 确保一个用户对一篇文章只有一条交互记录
        ordering = ["-updated_at"]

    def __str__(self):
        return f"用户 {self.user_id} 对文章 {self.article_id} 的交互"


# 创建Pydantic模型
Article_Pydantic = pydantic_model_creator(
    Article, name="Article"
)
ArticleCreate_Pydantic = pydantic_model_creator(
    Article, name="ArticleCreate", exclude=("id", "created_at", "updated_at")
)
