FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# PYTHONUNBUFFERED=1: 确保日志实时输出
# PYTHONPATH=/app: 设置模块搜索路径
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# 设置镜像源
RUN pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple

# 安装uv
RUN pip install --upgrade pip && pip install uv

# 启用字节码编译和优化链接模式
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy


COPY uv.lock pyproject.toml ./

# 安装依赖
RUN uv sync

COPY . .

# 激活虚拟环境
ENV PATH="/app/.venv/bin:$PATH"

# 声明暴露的端口
EXPOSE 8000

# 默认命令（可被 docker-compose 覆盖）
CMD ["granian", "--interface", "asgi", "main:create_app", "--host", "0.0.0.0", "--port", "8000", "--factory"]