FROM python:3.10-slim

# 1. 设置工作目录
WORKDIR /app

# 2. 先复制依赖文件并安装 (利用 Docker 缓存)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. 复制所有项目代码
COPY . .

# 4. 设置环境变量，为应用和 Render 提供关键信息
# 推荐 Python 不在缓冲输出，让日志能实时显示在 Render 上
ENV PYTHONUNBUFFERED=1
# 设置默认端口，方便本地测试，但会被 Render 自动覆盖
ENV PORT=8000

# 5. 声明端口 (仅为文档目的)
EXPOSE $PORT

# 6. 启动命令 (使用 shell 形式，以确保环境变量被正确解析)
#    这条命令会在启动失败时，将错误信息打印到控制台
CMD sh -c 'python -u main.py 2>&1 | tee /proc/1/fd/1'
