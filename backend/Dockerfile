# ---- 构建阶段：安装依赖 ----
FROM python:3.12-slim AS builder

# 安装 pip 工具
RUN pip install --upgrade pip

# 创建虚拟环境
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# 复制依赖文件并安装依赖
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ---- 最终阶段：运行应用 ----
FROM python:3.12-slim

# 安装运行时依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat-traditional && \
    rm -rf /var/lib/apt/lists/*

# 从构建阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 设置工作目录
WORKDIR /app

# 复制应用代码
COPY . .

# 声明暴露的端口
EXPOSE 8000

# 创建入口点脚本
RUN echo '#!/bin/sh\n\
set -e\n\
\n\
# 等待数据库准备就绪\n\
DB_PORT=${POSTGRES_PORT:-5432}\n\
echo "等待数据库连接..."\n\
while ! nc -z db ${DB_PORT}; do\n\
  echo "等待数据库连接..."\n\
  sleep 1\n\
done\n\
echo "数据库已就绪"\n\
\n\
# 执行传入的命令\n\
exec "$@"\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# 设置入口点
ENTRYPOINT ["/app/entrypoint.sh"]

# 默认命令（可被 docker-compose 覆盖）
CMD ["uvicorn", "main:create_app", "--host", "0.0.0.0", "--port", "8000", "--factory"]