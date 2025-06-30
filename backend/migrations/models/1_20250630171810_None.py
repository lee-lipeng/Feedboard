from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "feeds" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL /* 订阅源唯一ID */,
    "title" VARCHAR(255) /* 订阅源标题 */,
    "url" VARCHAR(512) NOT NULL UNIQUE /* 订阅源链接 */,
    "description" TEXT /* 订阅源描述 */,
    "website_url" VARCHAR(512) /* 订阅源官网链接 */,
    "image_url" VARCHAR(512) /* 订阅源图片链接 */,
    "category" VARCHAR(13) NOT NULL DEFAULT 'other' /* 订阅源分类 */,
    "last_fetched" TIMESTAMP /* 最后更新时间 */,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP /* 记录创建时间 */,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP /* 记录更新时间 */
);
CREATE TABLE IF NOT EXISTS "articles" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL /* 文章唯一ID */,
    "title" VARCHAR(255) NOT NULL /* 文章标题 */,
    "url" VARCHAR(512) NOT NULL UNIQUE /* 文章原始链接 */,
    "author" VARCHAR(255) /* 文章作者 */,
    "summary" TEXT /* 文章摘要或简介 */,
    "content" TEXT /* 文章完整内容（HTML格式） */,
    "image_url" VARCHAR(512) /* 文章特色图片链接 */,
    "published_at" TIMESTAMP /* 文章发布时间 */,
    "guid" VARCHAR(512) NOT NULL /* 文章全局唯一标识符 */,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP /* 记录创建时间 */,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP /* 记录更新时间 */,
    "feed_id" INT NOT NULL REFERENCES "feeds" ("id") ON DELETE CASCADE /* 所属订阅源 */
) /* 文章模型 - 代表一篇独立的新闻或博客文章。 */;
CREATE INDEX IF NOT EXISTS "idx_articles_publish_d5516c" ON "articles" ("published_at");
CREATE INDEX IF NOT EXISTS "idx_articles_guid_d408cf" ON "articles" ("guid");
CREATE TABLE IF NOT EXISTS "users" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL /* 用户ID */,
    "email" VARCHAR(255) NOT NULL UNIQUE /* 邮箱 */,
    "hashed_password" VARCHAR(255) NOT NULL /* 密码的哈希值 */,
    "is_active" INT NOT NULL DEFAULT 1 /* 是否激活 */,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP /* 创建时间 */,
    "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP /* 更新时间 */,
    "font_size" INT NOT NULL DEFAULT 100 /* 字体大小 */,
    "latest_articles_days" INT NOT NULL DEFAULT 7 /* 最新文章天数 */,
    "notifications_enabled" INT NOT NULL DEFAULT 1 /* 是否启用通知 */,
    "auto_refresh_enabled" INT NOT NULL DEFAULT 1 /* 是否启用自动刷新 */,
    "refresh_interval" INT NOT NULL DEFAULT 60 /* 刷新间隔（分钟） */,
    "default_sorting" VARCHAR(20) NOT NULL DEFAULT 'newest' /* 默认排序方式 */
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);
CREATE TABLE IF NOT EXISTS "UserFeed" (
    "feeds_id" INT NOT NULL REFERENCES "feeds" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS "uidx_UserFeed_feeds_i_f37f0b" ON "UserFeed" ("feeds_id", "user_id");
CREATE TABLE IF NOT EXISTS "UserArticle" (
    "articles_id" INT NOT NULL REFERENCES "articles" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
) /* 与此文章有交互的用户 */;
CREATE UNIQUE INDEX IF NOT EXISTS "uidx_UserArticle_article_ea4b66" ON "UserArticle" ("articles_id", "user_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
