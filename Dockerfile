# 使用官方 uv 镜像作为构建和运行环境
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 安装依赖（利用 uv.lock 确保版本一致）
RUN uv sync --frozen

# 运行脚本
# 提示：由于是监控类工具，这里直接运行 main.py
CMD ["uv", "run", "python", "main.py"]
