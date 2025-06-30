import xml.etree.ElementTree as ET
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Request
from fastapi.responses import Response
from arq.connections import ArqRedis
from collections import defaultdict
from loguru import logger

from models.user import User
from models.feed import UserFeed
from core.security import get_current_user

router = APIRouter()


@router.get("/export", response_class=Response, summary="导出OPML订阅文件")
async def export_opml_data(current_user: User = Depends(get_current_user)):
    """
    将当前用户的所有订阅数据打包成一个标准的 OPML 2.0 文件供下载。
    """
    user_feeds = await UserFeed.filter(user_id=current_user.id).prefetch_related('feed')

    opml = ET.Element('opml', version='2.0')
    head = ET.SubElement(opml, 'head')
    ET.SubElement(head, 'title').text = f"Feedboard Subscriptions for {current_user.email}"
    body = ET.SubElement(opml, 'body')

    feeds_by_category = defaultdict(list)
    for user_feed in user_feeds:
        category = user_feed.category.value if user_feed.category else "未分类"
        feeds_by_category[category].append(user_feed)

    for category, feeds in feeds_by_category.items():
        category_outline = ET.SubElement(body, 'outline', text=category, title=category)
        for user_feed in feeds:
            feed = user_feed.feed
            ET.SubElement(
                category_outline, 'outline', type='rss',
                text=user_feed.effective_title,
                title=user_feed.effective_title,
                xmlUrl=feed.url
            )

    opml_string = ET.tostring(opml, encoding='utf-8', method='xml').decode('utf-8')

    headers = {
        "Content-Disposition": "attachment; filename=\"feedboard_subscriptions.opml\"",
        "Content-Type": "application/xml; charset=utf-8"
    }

    logger.info(f"已成功为用户生成OPML文件 {current_user.email} ，共有 {len(user_feeds)} 订阅源.")
    return Response(content=opml_string, headers=headers)


@router.post("/import", status_code=status.HTTP_202_ACCEPTED, summary="从OPML文件导入订阅")
async def import_opml_data(
        request: Request,
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_user)
):
    """
    从用户上传的 OPML 文件中解析订阅信息，并在后台异步进行导入。
    """
    if not file.filename.endswith(('.opml', '.xml')):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="文件格式不支持，请上传 OPML 或 XML 文件。"
        )

    try:
        contents = await file.read()
        root = ET.fromstring(contents)
        body = root.find('body')
        if body is None:
            raise ValueError("OPML文件格式不正确，缺少 <body> 标签。")

        subscriptions_to_add = []
        for outline in body:
            if outline.tag == 'outline' and 'xmlUrl' not in outline.attrib:
                category = outline.get('text') or outline.get('title')
                for feed_outline in outline:
                    if 'xmlUrl' in feed_outline.attrib:
                        subscriptions_to_add.append(
                            {
                                "url": feed_outline.get('xmlUrl'),
                                "title_override": feed_outline.get('title') or feed_outline.get('text'),
                                "category": category.strip() if category else 'other'
                            }
                        )
            elif 'xmlUrl' in outline.attrib:
                subscriptions_to_add.append(
                    {
                        "url": outline.get('xmlUrl'),
                        "title_override": outline.get('title') or outline.get('text'),
                        "category": 'other'
                    }
                )

        if not subscriptions_to_add:
            raise ValueError("在文件中未找到有效的RSS订阅信息。")

        arq_pool: ArqRedis = request.app.state.arq_pool
        await arq_pool.enqueue_job(
            "import_feeds_for_user_task",
            user_id=current_user.id,
            subscriptions=subscriptions_to_add
        )

        return {"message": f"成功找到 {len(subscriptions_to_add)} 个订阅源，已开始在后台导入。"}

    except (ET.ParseError, ValueError) as e:
        logger.warning(f"无法解析OPML文件 {current_user.email}. 错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件解析失败: {e}"
        )
    except Exception as e:
        logger.exception(f"用户的OPML导入过程中发生意外错误 {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="导入过程中发生未知错误。"
        )