import uuid
from typing import Dict, Any
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from loguru import logger

from core.security import get_current_user_from_token

router = APIRouter()


class ConnectionManager:
    """
    负责管理所有活跃的WebSocket连接。
    它按用户ID组织连接，允许向特定用户的所有会话广播消息。
    """

    def __init__(self):
        # 存储活动连接: {user_id: {connection_id: websocket}}
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int, conn_id: str):
        """接受并存储一个新的WebSocket连接。"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = {}
        self.active_connections[user_id][conn_id] = websocket
        logger.info(f"用户 [{user_id}-{conn_id}] 已连接到WebSocket.")

    def disconnect(self, user_id: int, conn_id: str):
        """移除一个已断开的WebSocket连接。"""
        if user_id in self.active_connections and conn_id in self.active_connections[user_id]:
            del self.active_connections[user_id][conn_id]
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            logger.info(f"用户 [{user_id}-{conn_id}] 已断开WebSocket连接.")

    async def send_personal_message(self, message: Dict[str, Any], user_id: int):
        """向特定用户的所有活动连接发送JSON消息。"""
        if user_id in self.active_connections:
            # 创建副本以安全地迭代，因为disconnect会修改字典
            connections_to_notify = list(self.active_connections[user_id].items())
            logger.info(f"向用户 [{user_id}] 发送WebSocket消息: {message}")

            for conn_id, connection in connections_to_notify:
                try:
                    await connection.send_json(message)
                except (WebSocketDisconnect, RuntimeError):
                    logger.warning(f"WebSocket连接 [{user_id}-{conn_id}] 已断开，消息已丢弃.")
                    self.disconnect(user_id, conn_id)


manager = ConnectionManager()


@router.websocket("")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """
    WebSocket连接处理函数。
    处理连接认证、生命周期管理和消息收发。
    """
    conn_id = str(uuid.uuid4())

    # 将连接信息绑定到日志上下文
    with logger.contextualize(conn_id=conn_id):
        try:
            user = await get_current_user_from_token(token)
            if not user:
                logger.warning("WebSocket连接失败，无效令牌.")
                return

            await manager.connect(websocket, user.id, conn_id)
            logger.contextualize(user_id=user.id, user_email=user.email)

            await websocket.send_json(
                {
                    "type": "system",
                    "code": "CONNECTION_ESTABLISHED",
                    "message": "成功连接到实时通知服务"
                }
            )

            # 保持连接并监听消息
            while True:
                data = await websocket.receive_json()
                logger.debug(f"从客户端接收数据: {data}")
                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})

        except WebSocketDisconnect:
            logger.info("WebSocket连接已断开.")
        except Exception as e:
            logger.exception(f"WebSocket中发生意外错误: {e}")
            # 尝试向客户端发送错误信息
            try:
                await websocket.send_json(
                    {
                        "type": "error",
                        "code": "UNEXPECTED_ERROR",
                        "message": "服务器发生内部错误，连接已中断。"
                    }
                )
            except (WebSocketDisconnect, RuntimeError):
                logger.warning("无法向客户端发送错误消息，连接已关闭.")
        finally:
            if user:
                manager.disconnect(user.id, conn_id)
