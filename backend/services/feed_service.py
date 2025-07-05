from typing import List, Optional, Dict, Any
from datetime import datetime

import feedparser
import httpx
from loguru import logger
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import in_transaction

from models import Feed, UserFeed, FeedCategory, Article, UserArticle


async def parse_feed_from_url(url: str) -> Optional[dict]:
    """
    从给定的URL异步抓取并解析RSS源。

    Args:
        url: 要解析的RSS源的URL。

    Returns:
        包含解析后的源信息的字典，如果失败则返回None。
    """
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()

        feed_data = feedparser.parse(response.text)

        if feed_data.bozo:
            logger.warning(f"解析Feed时遇到问题 (bozo=1): {url}, 异常: {feed_data.bozo_exception}")

        feed_info = feed_data.get('feed', {})
        if not feed_info:
            logger.error(f"解析失败，无法从 {url} 中找到<feed>信息。")
            return None

        logger.success(f"成功解析Feed: {url}")
        return feed_info

    except httpx.HTTPStatusError as e:
        logger.error(f"从URL获取Feed时HTTP错误: {url}, 状态码: {e.response.status_code}")
        return None
    except Exception as e:
        logger.exception(f"从URL解析Feed时发生未知错误: {url}, 错误: {e}")
        return None


async def get_user_feeds(user_id: int) -> List[UserFeed]:
    """
    获取指定用户订阅的所有Feed源。

    Args:
        user_id: 用户的ID。

    Returns:
        一个包含用户订阅关系（UserFeed）对象的列表。
    """
    user_feeds = await UserFeed.filter(user_id=user_id).prefetch_related("feed").order_by("-created_at")
    logger.info(f"成功为用户ID {user_id} 检索到 {len(user_feeds)} 个订阅。")
    return user_feeds


async def get_feed(feed_id: int, user_id: int) -> Optional[Feed]:
    """
    获取单个订阅源的详细信息，前提是用户已订阅该源。

    Args:
        feed_id: 订阅源的ID。
        user_id: 用户的ID。

    Returns:
        Feed对象，如果未找到或用户未订阅则返回None。
    """
    try:
        # 验证用户是否订阅了此Feed
        user_feed = await UserFeed.get(user_id=user_id, feed_id=feed_id).prefetch_related("feed")
        logger.info(f"成功为用户 {user_id} 找到Feed {feed_id}")
        return user_feed.feed
    except DoesNotExist:
        logger.warning(f"获取Feed失败：用户 {user_id} 未订阅或Feed {feed_id} 不存在。")
        return None


async def create_feed(feed_data: dict, user_id: int) -> Feed:
    """
    为用户创建新的订阅关系。如果Feed已存在于数据库中，则只创建关联；
    如果Feed不存在，则先创建Feed，再创建关联。

    Args:
        feed_data: 包含 'url', 'title' (optional), 'category' (optional) 的字典。
        user_id: 用户的ID。

    Returns:
        与用户新订阅关系关联的Feed对象。

    Raises:
        ValueError: 如果用户已经订阅了此URL。
    """
    feed_url = str(feed_data["url"])

    # 1. 查找或创建Feed
    feed, created = await Feed.get_or_create(url=feed_url)
    if created:
        logger.info(f"数据库中未找到Feed，已创建新的Feed记录: {feed_url}")
        # 如果是新Feed，可以先用用户提供的信息填充，后台任务再更新
        feed.title = feed_data.get("title") or "处理中..."
        await feed.save()
    else:
        logger.info(f"Feed已存在于数据库中: {feed_url}")

    # 2. 检查用户是否已订阅
    if await UserFeed.filter(user_id=user_id, feed_id=feed.id).exists():
        logger.warning(f"用户 {user_id} 尝试重复订阅Feed: {feed_url}")
        raise ValueError("您已经订阅了此Feed")

    # 3. 创建用户与Feed的关联
    await UserFeed.create(
        user_id=user_id,
        feed_id=feed.id,
        title_override=feed_data.get("title"),
        category=feed_data.get("category", FeedCategory.OTHER)
    )
    logger.success(f"用户 [{user_id}] 成功订阅Feed: {feed_url}")

    return feed


async def delete_feed(feed_id: int, user_id: int) -> bool:
    """
    删除用户对某个Feed的订阅关系。

    Args:
        feed_id: 要取消订阅的Feed的ID。
        user_id: 用户的ID。

    Returns:
        如果成功删除返回True，否则返回False。
    """
    try:
        async with in_transaction():
            await UserFeed.filter(user_id=user_id, feed_id=feed_id).delete()
            if article_ids_to_check := await Article.filter(feed_id=feed_id).values_list("id", flat=True):
                await UserArticle.filter(
                    user_id=user_id,
                    article_id__in=article_ids_to_check
                ).delete()
            logger.success(f"成功为用户 {user_id} 取消订阅Feed ID: {feed_id}")
            return True
    except DoesNotExist:
        logger.warning(f"取消订阅失败：用户 {user_id} 未订阅Feed ID {feed_id} 或该Feed不存在。")
        return False


async def fetch_and_save_articles(feed: Feed, is_initial_fetch: bool = False) -> List[Article]:
    """
    获取并保存文章,并为所有订阅者创建关联记录
    """
    from api.ws import manager
    try:
        # 1. 首先获取所有订阅了此Feed的用户ID
        subscriber_ids = await UserFeed.filter(feed_id=feed.id).values_list('user_id', flat=True)

        # 2. 抓取Feed内容
        async with httpx.AsyncClient() as client:
            response = await client.get(feed.url, follow_redirects=True)
            response.raise_for_status()

        feed_data = feedparser.parse(response.content)

        # 3. 筛选并创建新文章
        newly_created_articles = []
        for entry in feed_data.entries:
            guid = entry.get("id", entry.get("link"))
            if not guid:
                continue

            existing_article = await Article.get_or_none(guid=guid, feed_id=feed.id)
            # 如果文章已存在，跳过
            if existing_article:
                continue

            published_at = datetime(*entry.published_parsed[:6]) if "published_parsed" in entry else datetime.now()

            article = await Article.create(
                title=entry.get("title", "无标题"),
                url=entry.get("link", ""),
                author=entry.get("author"),
                summary=entry.get("summary"),
                content=entry.get("content", [{}])[0].get("value"),
                image_url=extract_image_url(entry),
                published_at=published_at,
                guid=guid,
                feed=feed
            )
            newly_created_articles.append(article)

        # 4. 如果有新文章且订阅者列表不为空，为所有订阅者批量创建关联记录
        if newly_created_articles and subscriber_ids:
            user_article_links = [
                UserArticle(user_id=user_id, article_id=article.id)
                for article in newly_created_articles
                for user_id in subscriber_ids
            ]
            await UserArticle.bulk_create(user_article_links)
            feed_title = feed.title or "未命名订阅源"

            # 5. 向订阅者发送新文章通知
            if not is_initial_fetch:
                for user_id in subscriber_ids:
                    await manager.send_personal_message(
                        {
                            "type": "new_articles",
                            "message": f"你订阅的 [{feed_title}-{feed.url}] 有{len(newly_created_articles)}篇新文章发布！",
                            "feed_id": feed.id,
                            "count": len(newly_created_articles)
                        }, user_id
                    )

        # 6. 更新Feed的最后获取时间
        feed.last_fetched = datetime.now()
        await feed.save()

        return newly_created_articles
    except Exception as e:
        logger.exception(f"抓取Feed {feed.url} 失败: {e}")
        return []


def extract_image_url(entry: Dict[str, Any]) -> Optional[str]:
    """
    从Feed条目中提取图片URL
    """
    # 尝试从媒体内容中获取图片URL
    if "media_content" in entry:
        for media in entry["media_content"]:
            if "medium" in media and media["medium"] == "image":
                return media["url"]
            elif "type" in media and media["type"].startswith("image/"):
                return media["url"]

    # 尝试从封面图片中获取
    if "media_thumbnail" in entry and entry["media_thumbnail"]:
        return entry["media_thumbnail"][0]["url"]

    # 尝试从内容中提取图片URL
    if "content" in entry and entry["content"]:
        content = entry["content"][0]["value"]
        img_start = content.find("<img")
        if img_start != -1:
            src_start = content.find("src=\"", img_start)
            if src_start != -1:
                src_start += 5
                src_end = content.find("\"", src_start)
                if src_end != -1:
                    return content[src_start:src_end]

    # 如果以上都失败，尝试从摘要中提取
    if "summary" in entry:
        content = entry["summary"]
        img_start = content.find("<img")
        if img_start != -1:
            src_start = content.find("src=\"", img_start)
            if src_start != -1:
                src_start += 5
                src_end = content.find("\"", src_start)
                if src_end != -1:
                    return content[src_start:src_end]

    return None
