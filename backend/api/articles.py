import math
from typing import Dict, Optional, List
from datetime import datetime

from pydantic import BaseModel
from loguru import logger
from fastapi import APIRouter, Depends, Query, HTTPException, status

from models.user import User
from core.security import get_current_user
from services.article_service import (
    get_user_articles,
    get_article_detail,
    update_article_status,
    mark_all_articles_as_read,
    search_user_articles,
)

router = APIRouter()


class ArticleStatusUpdate(BaseModel):
    """更新文章状态的请求体模型。"""
    is_read: Optional[bool] = None
    is_favorite: Optional[bool] = None
    read_later: Optional[bool] = None
    read_position: Optional[int] = None


class ArticleResponse(BaseModel):
    """单个文章的响应模型，包含用户交互状态。"""
    id: int
    title: str
    url: str
    author: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    published_at: Optional[datetime] = None
    feed_id: int
    feed_title: str
    is_read: bool
    is_favorite: bool
    read_later: bool
    read_position: int
    created_at: datetime
    updated_at: datetime


class PaginatedArticleResponse(BaseModel):
    """文章列表的分页响应模型。"""
    data: List[ArticleResponse]
    total: int
    page: int
    total_pages: int
    has_more: bool


@router.get("", response_model=PaginatedArticleResponse, summary="获取文章列表")
async def list_articles(
        skip: int = Query(0, ge=0, description="分页偏移量"),
        limit: int = Query(20, ge=1, le=100, description="每页数量"),
        feed_id: Optional[int] = Query(None, description="按特定订阅源ID过滤"),
        is_read: Optional[bool] = Query(None, description="按已读状态过滤"),
        is_favorite: Optional[bool] = Query(None, description="按收藏状态过滤"),
        read_later: Optional[bool] = Query(None, description="按稍后读状态过滤"),
        sort_by: str = Query("published_at", description="排序字段，如 'published_at'"),
        current_user: User = Depends(get_current_user),
):
    """
    获取当前用户的文章列表，支持丰富的过滤、排序和分页功能。
    所有业务逻辑已移至服务层。
    """
    logger.info(f"用户 {current_user.id} 正在获取文章列表，参数: feed_id={feed_id}, is_read={is_read}, sort_by={sort_by}")

    articles, total = await get_user_articles(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        feed_id=feed_id,
        is_read=is_read,
        is_favorite=is_favorite,
        read_later=read_later,
        sort_by=sort_by,
    )

    total_pages = math.ceil(total / limit) if limit > 0 else 0
    page = (skip // limit) + 1 if limit > 0 else 1

    return {
        "data": articles,
        "total": total,
        "page": page,
        "total_pages": total_pages,
        "has_more": page < total_pages,
    }


@router.get("/search", response_model=PaginatedArticleResponse, summary="搜索文章")
async def search_articles(
        q: str = Query(..., min_length=1, max_length=100, description="搜索关键词"),
        skip: int = Query(0, ge=0, description="分页偏移量"),
        limit: int = Query(20, ge=1, le=100, description="每页数量"),
        current_user: User = Depends(get_current_user),
):
    """
    根据关键词在当前用户订阅的所有文章中进行全文搜索。
    """
    if not q.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="搜索关键词不能为空")

    articles, total = await search_user_articles(user_id=current_user.id, query=q, skip=skip, limit=limit)
    total_pages = math.ceil(total / limit) if limit > 0 else 0
    page = (skip // limit) + 1 if limit > 0 else 1

    logger.success(f"为用户 {current_user.id} 的搜索 '{q}' 找到 {total} 篇文章。")
    return {
        "data": articles,
        "total": total,
        "page": page,
        "total_pages": total_pages,
        "has_more": page < total_pages,
    }


@router.get("/{article_id}", response_model=ArticleResponse, summary="获取单篇文章详情")
async def read_article(
        article_id: int,
        current_user: User = Depends(get_current_user)
):
    """
    获取指定ID的单篇文章详情，包括其内容和用户交互状态。
    如果用户首次查看，文章会自动标记为已读。
    """
    article = await get_article_detail(article_id=article_id, user_id=current_user.id)
    if not article:
        logger.warning(f"用户 {current_user.id} 请求的文章 (ID: {article_id}) 未找到或无权访问。")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在或您没有权限查看")

    logger.success(f"成功返回文章 (ID: {article_id}) 的详情给用户 {current_user.id}")
    return article


@router.patch("/{article_id}/status", response_model=Dict, summary="更新文章状态")
async def update_article_status_endpoint(
        article_id: int,
        status_update: ArticleStatusUpdate,
        current_user: User = Depends(get_current_user)
):
    """
    更新单篇文章的用户特定状态，如已读、收藏、稍后读或阅读位置。
    """
    result = await update_article_status(
        article_id=article_id,
        user_id=current_user.id,
        is_read=status_update.is_read,
        is_favorite=status_update.is_favorite,
        read_later=status_update.read_later,
        read_position=status_update.read_position
    )

    if not result:
        logger.warning(f"用户 {current_user.id} 更新文章状态失败 (ID: {article_id})，文章可能不存在或无权访问。")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在或更新失败")

    logger.success(f"成功为用户 {current_user.id} 更新了文章 (ID: {article_id}) 的状态:{status_update}。")
    return result


@router.post("/mark-all-read", summary="全部标记为已读")
async def mark_all_as_read(
        feed_id: Optional[int] = Query(None, description="指定要操作的订阅源ID，如果为空则操作全部"),
        current_user: User = Depends(get_current_user)
):
    """
    将指定订阅源或全部订阅源的所有文章标记为已读。
    这是一个高效的批量操作。
    """
    count = await mark_all_articles_as_read(user_id=current_user.id, feed_id=feed_id)

    message = f"成功将 {count} 篇文章标记为已读"
    logger.success(f"为用户 {current_user.id} 操作完成: {message}")
    return {"message": message, "count": count}
