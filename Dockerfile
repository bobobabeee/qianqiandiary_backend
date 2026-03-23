# 使用官方 Python 3.12 镜像作为基础
FROM python:3.12-slim
# 调整时区
RUN rm -f /etc/localtime \
&& ln -sv /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
&& echo "Asia/Shanghai" > /etc/timezone
# 设置工作目录
WORKDIR /app

# 复制当前目录下的所有文件到容器的 /app 目录
COPY . .

# 安装依赖
RUN pip install -r requirements.txt

# 暴露端口 8080
EXPOSE 8080

# 启动命令
CMD ["python3", "app.py"]