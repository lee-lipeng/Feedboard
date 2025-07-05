import re
from typing import List, Optional, Dict, Tuple

import httpx
from loguru import logger

from tortoise.expressions import Q
from models import Article, UserArticle, UserFeed


async def get_user_articles(
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        feed_id: Optional[int] = None,
        is_read: Optional[bool] = None,
        is_favorite: Optional[bool] = None,
        read_later: Optional[bool] = None,
        sort_by: str = "published_at"  # 新增排序参数
) -> Tuple[List[Dict], int]:
    """
    获取用户的文章列表，支持多种过滤条件和排序。

    Args:
        user_id: 用户ID。
        skip: 分页偏移量。
        limit: 每页数量。
        feed_id: 按特定Feed源ID过滤。
        is_read: 按已读状态过滤。
        is_favorite: 按收藏状态过滤。
        read_later: 按稍后读状态过滤。
        sort_by: 排序字段 (如 'published_at', 'created_at')。

    Returns:
        一个元组，包含文章字典列表和符合条件的总文章数。
    """
    # 核心查询：基于 UserArticle，因为它链接了所有信息
    query = UserArticle.filter(user_id=user_id)

    # 应用过滤条件
    if feed_id:
        query = query.filter(article__feed_id=feed_id)
    if is_read is not None:
        query = query.filter(is_read=is_read)
    if is_favorite is not None:
        query = query.filter(is_favorite=is_favorite)
    if read_later is not None:
        query = query.filter(read_later=read_later)

    # 获取总数
    total = await query.count()

    # 应用排序
    # Tortoise ORM 使用 `article__published_at` 来引用关联模型的字段
    order = f"-article__{sort_by}" if sort_by.startswith("published") else f"-{sort_by}"

    # 获取分页后的数据，并预加载关联数据以避免N+1查询
    user_articles = await query.order_by(order).offset(skip).limit(limit).prefetch_related("article", "article__feed")

    # 构建响应数据
    result = []
    for ua in user_articles:
        article = ua.article
        result.append(
            {
                "id": article.id,
                "title": article.title,
                "url": article.url,
                "author": article.author,
                "summary": article.summary,
                "content": article.content,
                "image_url": article.image_url,
                "published_at": article.published_at,
                "guid": article.guid,
                "feed_id": article.feed_id,
                "feed_title": article.feed.title,
                "is_read": ua.is_read,
                "is_favorite": ua.is_favorite,
                "read_later": ua.read_later,
                "read_position": ua.read_position,
                "created_at": article.created_at,
                "updated_at": article.updated_at
            }
        )

    logger.info(f"为用户 {user_id} 找到 {len(result)} 篇文章（总计 {total} 篇）。")
    return result, total


async def get_article_detail(article_id: int, user_id: int) -> Optional[Dict]:
    """
    获取单篇文章的详细信息，同时包含用户对该文章的交互状态。
    在获取前会验证用户是否有权限查看该文章（即是否订阅了该文章的源）。
    首次查看时，会自动将文章标记为已读。
    """
    article = await Article.get_or_none(id=article_id).prefetch_related("feed")
    if not article:
        logger.warning(f"获取文章详情失败：未找到文章ID {article_id}")
        return None

    # 验证用户是否订阅了该文章的源
    if not await UserFeed.filter(user_id=user_id, feed_id=article.feed_id).exists():
        logger.warning(f"权限拒绝：用户 {user_id} 尝试访问未订阅源 (Feed ID: {article.feed_id}) 的文章 (Article ID: {article_id})")
        return None

    user_article = await UserArticle.get_or_none(user_id=user_id, article_id=article.id)

    # 构造带有用户状态的文章信息
    article_dict = {
        "id": article.id,
        "title": article.title,
        "url": article.url,
        "author": article.author,
        "summary": article.summary,
        "content": article.content,
        "image_url": article.image_url,
        "published_at": article.published_at.isoformat() if article.published_at else None,
        "guid": article.guid,
        "feed_id": article.feed_id,
        "feed_title": article.feed.title,
        "is_read": user_article.is_read if user_article else False,
        "is_favorite": user_article.is_favorite if user_article else False,
        "read_later": user_article.read_later if user_article else False,
        "read_position": user_article.read_position if user_article else 0,
        "created_at": article.created_at,
        "updated_at": article.updated_at
    }

    # 如果是首次查看，自动标记为已读
    if not user_article or not user_article.is_read:
        logger.info(f"用户 {user_id} 首次查看文章 {article_id}，自动标记为已读。")
        await update_article_status(article_id, user_id, is_read=True)
        article_dict["is_read"] = True

    return article_dict


async def update_article_status(
        article_id: int,
        user_id: int,
        is_read: Optional[bool] = None,
        is_favorite: Optional[bool] = None,
        read_later: Optional[bool] = None,
        read_position: Optional[int] = None
) -> Optional[Dict]:
    """
    更新用户对特定文章的交互状态（如已读、收藏等）。
    """
    article = await Article.get_or_none(id=article_id)
    if not article:
        logger.warning(f"更新状态失败：未找到文章ID {article_id}")
        return None

    # 验证用户权限
    if not await UserFeed.filter(user_id=user_id, feed_id=article.feed_id).exists():
        logger.warning(f"权限拒绝：用户 {user_id} 尝试更新未订阅源的文章 {article_id}")
        return None

    # 获取或创建用户文章交互记录
    user_article, _ = await UserArticle.get_or_create(user_id=user_id, article_id=article_id)

    # 逐个检查并更新字段
    updated_fields = []
    if is_read is not None and user_article.is_read != is_read:
        user_article.is_read = is_read
        updated_fields.append("is_read")

    if is_favorite is not None and user_article.is_favorite != is_favorite:
        user_article.is_favorite = is_favorite
        updated_fields.append("is_favorite")

    if read_later is not None and user_article.read_later != read_later:
        user_article.read_later = read_later
        updated_fields.append("read_later")

    if read_position is not None and user_article.read_position != read_position:
        user_article.read_position = read_position
        updated_fields.append("read_position")

    if updated_fields:
        await user_article.save(update_fields=updated_fields)
        logger.info(f"成功为用户 {user_id} 更新了文章 {article_id} 的状态: {updated_fields}")

    # 返回更新后的完整状态
    return {
        "article_id": article_id,
        "is_read": user_article.is_read,
        "is_favorite": user_article.is_favorite,
        "read_later": user_article.read_later,
        "read_position": user_article.read_position
    }


async def mark_all_articles_as_read(user_id: int, feed_id: Optional[int] = None) -> int:
    """
    将指定Feed或所有Feed的文章全部标记为已读。此操作经过优化，高效执行。
    它会为从未交互过的文章创建新的已读记录，并更新已存在但未读的记录。
    
    Args:
        user_id: 用户的ID。
        feed_id: 可选，要操作的特定Feed的ID。如果为None，则操作用户的所有订阅。
        
    Returns:
        成功标记为已读的文章总数。
    """
    # 1. 确定要操作的文章ID范围
    article_query = Article.filter()
    if feed_id:
        if not await UserFeed.filter(user_id=user_id, feed_id=feed_id).exists():
            logger.warning(f"权限拒绝：用户 {user_id} 尝试对未订阅的Feed ID {feed_id} 进行全部已读操作。")
            return 0
        article_query = article_query.filter(feed_id=feed_id)
    else:
        subscribed_feed_ids = await UserFeed.filter(user_id=user_id).values_list('feed_id', flat=True)
        if not subscribed_feed_ids:
            return 0  # 用户没有任何订阅
        article_query = article_query.filter(feed_id__in=subscribed_feed_ids)

    all_article_ids = await article_query.values_list('id', flat=True)
    if not all_article_ids:
        return 0  # 订阅中没有任何文章

    # 2. 查找用户已经存在的交互记录
    existing_ua_query = UserArticle.filter(user_id=user_id, article_id__in=all_article_ids)
    existing_ua_article_ids = await existing_ua_query.values_list('article_id', flat=True)

    # 3. 计算哪些文章需要创建新的UserArticle记录
    new_record_article_ids = set(all_article_ids) - set(existing_ua_article_ids)

    # 4. 批量创建新的记录，并直接标记为已读
    if new_record_article_ids:
        new_records = [UserArticle(user_id=user_id, article_id=art_id, is_read=True) for art_id in new_record_article_ids]
        await UserArticle.bulk_create(new_records)
        logger.info(f"为用户 {user_id} 创建并标记了 {len(new_record_article_ids)} 篇新文章为已读。")

    # 5. 批量更新已存在但未读的记录
    rows_updated = await existing_ua_query.filter(is_read=False).update(is_read=True)
    if rows_updated > 0:
        logger.info(f"为用户 {user_id} 更新了 {rows_updated} 篇已有文章为已读。")

    total_affected = len(new_record_article_ids) + rows_updated
    if total_affected > 0:
        logger.success(f"操作完成：共为用户 {user_id} 标记了 {total_affected} 篇文章为已读。")
    else:
        logger.info(f"操作完成：用户 {user_id} 的所有相关文章均已是已读状态。")

    return total_affected


async def search_user_articles(user_id: int, query: str, skip: int = 0, limit: int = 20) -> Tuple[List[Dict], int]:
    """
    在用户的订阅文章中进行全文搜索（标题、摘要和内容）。
    该实现经过优化，可有效执行搜索和分页。
    """
    # 1. 确定用户的订阅范围
    subscribed_feed_ids = await UserFeed.filter(user_id=user_id).values_list('feed_id', flat=True)
    if not subscribed_feed_ids:
        logger.debug(f"用户 {user_id} 没有任何订阅，搜索结果为空。")
        return [], 0

    # 2. 构建搜索查询，直接在文章表上进行
    search_query = Article.filter(feed_id__in=subscribed_feed_ids).filter(
        Q(title__icontains=query) | Q(summary__icontains=query) | Q(content__icontains=query)
    )

    # 3. 获取总数用于分页
    total = await search_query.count()

    # 4. 获取分页后的文章数据
    articles = await search_query.prefetch_related("feed").order_by("-published_at").offset(skip).limit(limit)

    # 5. 批量获取这些文章的用户交互状态，以避免N+1查询
    article_ids = [article.id for article in articles]
    user_articles_map = {
        ua.article_id: ua for ua in await UserArticle.filter(user_id=user_id, article_id__in=article_ids)
    }

    # 6. 构建最终响应数据
    result = []
    for article in articles:
        user_article = user_articles_map.get(article.id)
        result.append(
            {
                "id": article.id,
                "title": article.title,
                "url": article.url,
                "content": article.content,  # 在搜索结果中直接返回内容
                "author": article.author,
                "summary": article.summary,
                "published_at": article.published_at.isoformat() if article.published_at else None,
                "feed_id": article.feed_id,
                "feed_title": article.feed.title,
                "is_read": user_article.is_read if user_article else False,
                "is_favorite": user_article.is_favorite if user_article else False,
                "read_later": user_article.read_later if user_article else False,
                "read_position": user_article.read_position if user_article else 0,
                "created_at": article.created_at,
                "updated_at": article.updated_at
            }
        )

    logger.info(f"为用户 {user_id} 的搜索 '{query}' 找到了 {total} 篇文章，返回 {len(result)} 篇。")
    return result, total


async def fetch_article_content(article: Article) -> str:
    """
    获取文章的完整HTML内容。如果数据库中已缓存，则直接返回；否则，从源URL抓取并缓存。
    """
    if article.content and len(article.content) > 100:  # 假设内容过短的都是摘要
        logger.debug(f"返回文章 {article.id} 的缓存内容。")
        return article.content

    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            response = await client.get(article.url)
            response.raise_for_status()

        body_content = extract_main_body(response.text) or article.summary

        if body_content:
            article.content = body_content
            await article.save(update_fields=['content'])
            logger.success(f"成功抓取并缓存了文章 {article.id} 的内容。")
            return body_content

        return article.summary or "无法获取文章的有效内容。"
    except httpx.HTTPStatusError as e:
        logger.error(f"抓取文章 {article.id} 内容时发生HTTP错误: {e.response.status_code}")
        return article.summary or f"获取文章内容失败: 服务器返回 {e.response.status_code}"
    except Exception as e:
        logger.exception(f"抓取文章 {article.id} 内容时发生未知错误: {e}")
        return article.summary or "获取文章内容时发生未知错误。"


def extract_main_body(html_content: str) -> Optional[str]:
    """
    一个简化的、基于正则表达式规则的HTML正文提取器。
    它会尝试多个常见的文章容器标签和class/id名称。
    """
    # 移除脚本和样式，减少干扰
    cleaned_html = re.sub(r'<(script|style)\b[^>]*>.*?</\1>', '', html_content, flags=re.DOTALL | re.IGNORECASE)

    # 定义一系列可能的正文容器模式
    content_patterns = [
        r'<article\b[^>]*>(.*?)</article>',
        r'<main\b[^>]*>(.*?)</main>',
        r'<div\b[^>]*?(?:id|class)=["\'](?:article|content|main|post|body|entry-content)["\'][^>]*>(.*?)</div>'
    ]

    for pattern in content_patterns:
        match = re.search(pattern, cleaned_html, re.DOTALL | re.IGNORECASE)
        if match:
            # 返回第一个匹配到的、最可能的内容
            return match.group(1).strip()

    # 如果以上模式都未匹配，则返回None
    return None
