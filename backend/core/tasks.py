import tortoise
from typing import Dict, Any
from datetime import datetime
from arq.connections import RedisSettings
from arq import cron
from loguru import logger

from core.config import settings
from models.feed import Feed
from services.feed_service import parse_feed_from_url, fetch_and_save_articles, get_user_feeds, create_feed
from api.ws import manager


async def setup_db(ctx):
    """
    ARQ任务需要独立初始化数据库连接
    """
    # ctx是arq传递的上下文，可以用来存储连接
    if not ctx.get('tortoise_initialized'):
        logger.info("初始化数据库连接...")
        await tortoise.Tortoise.init(
            db_url=settings.DATABASE_URI,
            modules={"models": settings.DB_MODELS}
        )
        ctx['tortoise_initialized'] = True


async def cleanup_db(ctx):
    """
    清理数据库连接
    """
    if ctx.get('tortoise_initialized'):
        logger.info("关闭数据库连接...")
        await tortoise.Tortoise.close_connections()
        ctx['tortoise_initialized'] = False


async def process_new_feed_task(ctx: Dict[str, Any], feed_id: int, user_id: int):
    """
    后台任务：解析Feed信息，抓取文章，并通知用户。
    """
    await setup_db(ctx)
    feed = await Feed.get_or_none(id=feed_id)
    if not feed:
        return

    try:
        # 1. 解析Feed信息并更新Feed对象
        if feed_info := await parse_feed_from_url(feed.url):
            feed.title = feed_info.get("title", "未命名订阅源")
            feed.description = feed_info.get("description")
            feed.website_url = feed_info.get("website_url")
            feed.image_url = feed_info.get("image_url")
            await feed.save()

        # 2. 获取并创建文章
        new_articles = await fetch_and_save_articles(feed, is_initial_fetch=True)

        # 3. 通知发起操作的用户
        message = f"订阅源 '{feed.title}' 添加成功"
        if new_articles:
            message += f"，已抓取 {len(new_articles)} 篇新文章。"
        else:
            message += "，暂无新文章。"

        await manager.send_personal_message(
            {
                "type": "feed_processed",
                "message": message,
                "feed_id": feed.id
            }, user_id
        )

    except Exception as e:
        # 异常处理：通知用户失败
        await manager.send_personal_message(
            {
                "type": "error",
                "message": f"处理订阅源 '{feed.url}' 时出错: {e}",
            }, user_id
        )


async def refresh_all_feeds_task(ctx: Dict[str, Any]):
    """
    定时任务：更新所有订阅源的文章
    """
    await setup_db(ctx)
    logger.info(f"[{datetime.now()}] 开始执行定时任务：刷新所有Feed...")
    feeds = await Feed.all()

    for feed in feeds:
        try:
            await fetch_and_save_articles(feed)
        except Exception as e:
            logger.error(f"刷新 Feed '{feed.title}' ({feed.id}) 时出错: {e}")

    logger.info(f"[{datetime.now()}] 定时任务执行完毕。")


async def refresh_single_feed_task(ctx: Dict[str, Any], feed_id: int):
    """
    后台任务：刷新单个订阅源
    """
    await setup_db(ctx)
    if feed := await Feed.get_or_none(id=feed_id):
        try:
            logger.info(f"开始刷新 Feed '{feed.title}' ({feed.id})...")
            await fetch_and_save_articles(feed)
        except Exception as e:
            logger.error(f"刷新 Feed '{feed.title}' ({feed.id})失败: {e}")


async def refresh_all_feeds_for_user(ctx: Dict[str, Any], user_id: int):
    """
    为指定用户刷新其所有订阅源，通过为每个源创建独立的后台任务
    """
    await setup_db(ctx)
    arq_pool = ctx['redis']
    user_feeds = await get_user_feeds(user_id)
    count = 0
    for user_feed in user_feeds:
        await arq_pool.enqueue_job("refresh_single_feed_task", feed_id=user_feed.feed.id)
        count += 1



async def import_feeds_for_user_task(ctx: Dict[str, Any], user_id: int, subscriptions: list):
    """
    后台任务：为用户批量导入订阅源
    """
    await setup_db(ctx)
    arq_pool = ctx['redis']

    success_count = 0
    failure_count = 0

    for sub in subscriptions:
        try:
            # 复用已有的 create_feed 逻辑
            feed = await create_feed({"url": sub["url"], "title": sub.get("title_override"), "category": sub.get("category")}, user_id)
            # 为新创建的 feed 触发后台抓取任务
            await arq_pool.enqueue_job("process_new_feed_task", feed_id=feed.id, user_id=user_id)
            success_count += 1
        except ValueError:  # 忽略已存在的订阅
            success_count += 1
        except Exception as e:
            print(f"导入订阅源 {sub['url']} 时失败: {e}")
            failure_count += 1

    # 任务完成后通知用户
    await manager.send_personal_message(
        {
            "type": "import_completed",
            "message": f"订阅导入完成！成功: {success_count}, 失败: {failure_count}。",
        }, user_id
    )


async def startup(ctx: Dict[str, Any]):
    """
    Worker 启动时执行
    """
    ctx['tortoise_initialized'] = False
    logger.info("ARQ Worker 启动...")


async def shutdown(ctx: Dict[str, Any]):
    """
    Worker 关闭时执行
    """
    await cleanup_db(ctx)
    logger.info("ARQ Worker 关闭...")


class WorkerSettings:
    """
    ARQ Worker配置
    """
    redis_settings = RedisSettings(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD or None,
        database=settings.REDIS_DB
    )
    functions = [
        process_new_feed_task,
        refresh_all_feeds_task,
        refresh_all_feeds_for_user,
        refresh_single_feed_task,
        import_feeds_for_user_task
    ]
    on_startup = startup
    on_shutdown = shutdown
    cron_jobs = [
        cron(
            'refresh_all_feeds_task',
            minute={0, 30},  # 每30分钟执行
            run_at_startup=True  # 启动时立即执行一次
        )
    ]

# 启动：arq core.tasks.WorkerSettings
