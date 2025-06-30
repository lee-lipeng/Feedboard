from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, HttpUrl
from arq.connections import ArqRedis
from loguru import logger
from datetime import datetime

from models.user import User
from models.feed import FeedCategory
from core.security import get_current_user
from services.feed_service import (
    get_user_feeds,
    get_feed,
    create_feed,
    delete_feed
)

router = APIRouter()


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


class FeedCreate(BaseModel):
    """创建新订阅时客户端发送的数据模型。"""
    url: HttpUrl
    title: Optional[str] = None
    category: FeedCategory = FeedCategory.OTHER


@router.get("", response_model=List[UserFeedResponse])
async def read_feeds(
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取当前认证用户的所有订阅源。
    """
    user_feeds = await get_user_feeds(current_user.id)

    # 手动构建包含完整Feed信息的响应模型列表
    result = []
    for user_feed in user_feeds[skip:skip + limit]:
        feed = user_feed.feed
        result.append(
            UserFeedResponse(
                id=user_feed.id,
                title_override=user_feed.title_override,
                category=user_feed.category,
                created_at=user_feed.created_at,
                updated_at=user_feed.updated_at,
                feed_id=feed.id,
                feed_title=feed.title,
                feed_url=feed.url,
                feed_description=feed.description,
                feed_website_url=feed.website_url,
                feed_image_url=feed.image_url,
                feed_last_fetched=feed.last_fetched
            )
        )

    logger.success(f"成功为用户 {current_user.id} 返回 {len(result)} 个订阅源。")
    return result


@router.post("", response_model=FeedResponse, status_code=status.HTTP_202_ACCEPTED)
async def add_feed_subscription(
        request: Request,
        feed_in: FeedCreate,
        current_user: User = Depends(get_current_user)
) -> Any:
    """
    为当前用户添加一个新的Feed订阅。
    此操作是异步的：API会立即返回，并在后台通过arq任务处理Feed的抓取和解析。
    """
    try:
        # 该服务函数只处理快速的数据库操作（创建关系）
        feed = await create_feed(feed_in.model_dump(), current_user.id)

        # 将耗时的抓取和解析操作放入arq任务队列
        arq_pool: ArqRedis = request.app.state.arq_pool
        await arq_pool.enqueue_job("process_new_feed_task", feed_id=feed.id, user_id=current_user.id)
        logger.info(f"已为Feed ID {feed.id} 创建后台解析任务。")

        # 立即返回一个临时响应
        return FeedResponse(
            feed_id=feed.id,
            feed_title=feed.title or "处理中...",
            feed_url=feed.url,
            feed_description="正在后台处理...",
            feed_website_url=None,
            feed_image_url=None,
            feed_last_fetched=None,
            feed_category=feed_in.category,
            feed_created_at=feed.created_at,
            feed_updated_at=feed.updated_at
        )
    except ValueError as e:
        # 捕获由服务层抛出的特定错误，例如"已经订阅"
        logger.warning(f"用户 {current_user.id} 添加订阅失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{feed_id}", response_model=FeedResponse)
async def read_feed(
        feed_id: int,
        current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取单个订阅源的详细信息。
    """
    feed = await get_feed(feed_id, current_user.id)
    if not feed:
        logger.warning(f"用户 {current_user.id} 请求的Feed (ID: {feed_id}) 未找到或无权访问。")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="您未订阅此Feed，或该Feed不存在。"
        )

    logger.success(f"成功返回Feed (ID: {feed_id}) 的详情给用户 {current_user.id}。")
    return FeedResponse.model_validate(feed)


@router.delete("/{feed_id}", status_code=status.HTTP_200_OK)
async def remove_feed(
        feed_id: int,
        current_user: User = Depends(get_current_user)
) -> Any:
    """
    为当前用户取消订阅一个Feed源。
    """
    deleted = await delete_feed(feed_id, current_user.id)
    if not deleted:
        logger.warning(f"用户 {current_user.id} 取消订阅失败，因为未订阅Feed ID {feed_id}。")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="取消订阅失败：您未订阅此Feed。"
        )
    logger.success(f"用户 {current_user.id} 已成功取消订阅Feed ID {feed_id}。")
    return {"status": "success", "message": "已成功取消订阅"}


@router.post("/refresh-all", status_code=status.HTTP_202_ACCEPTED)
async def refresh_all_feeds_for_current_user(
        request: Request,
        current_user: User = Depends(get_current_user)
) -> Any:
    """
    为当前用户触发所有订阅源的后台刷新任务。
    这是一个异步操作，会立即返回。
    """
    logger.info(f"用户 {current_user.id} 触发了所有订阅源的后台刷新。")
    arq_pool: ArqRedis = request.app.state.arq_pool
    await arq_pool.enqueue_job("refresh_all_feeds_for_user", user_id=current_user.id)
    return {"message": "已成功触发所有订阅源的后台刷新任务"}


@router.post("/{feed_id}/refresh", status_code=status.HTTP_202_ACCEPTED)
async def refresh_feed(
        request: Request,
        feed_id: int,
        current_user: User = Depends(get_current_user)
) -> Any:
    """
    为当前用户手动触发单个订阅源的后台刷新。
    """
    feed = await get_feed(feed_id, current_user.id)
    if not feed:
        logger.warning(f"用户 {current_user.id} 尝试刷新一个不存在或未订阅的Feed (ID: {feed_id})。")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="您未订阅此Feed，或该Feed不存在。"
        )

    # 将刷新任务放入arq队列
    arq_pool: ArqRedis = request.app.state.arq_pool
    await arq_pool.enqueue_job("process_new_feed_task", feed_id=feed.id, user_id=current_user.id)

    logger.success(f"已为Feed (ID: {feed.id}) 创建后台刷新任务。")
    return {"message": f"已触发 '{feed.title}' 的后台刷新"}
