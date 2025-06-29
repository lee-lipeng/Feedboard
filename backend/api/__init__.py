from fastapi import APIRouter

from . import auth, users, feeds, articles, ws, preferences, data

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(feeds.router, prefix="/feeds", tags=["订阅源"])
api_router.include_router(articles.router, prefix="/articles", tags=["文章详情"])
api_router.include_router(ws.router, prefix="/ws", tags=["websocket"])
api_router.include_router(preferences.router, prefix="/preferences", tags=["偏好设置"])
api_router.include_router(data.router, prefix="/data", tags=["数据导入导出"])
