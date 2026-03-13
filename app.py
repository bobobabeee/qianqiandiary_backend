from app import create_app

# 创建应用实例（指定环境：dev开发/ prod生产）
app = create_app(config_name="dev")
# app = create_app(config_name="prod")

if __name__ == "__main__":
    # 启动服务，host=0.0.0.0允许外部访问，port指定端口
    app.run(host="0.0.0.0", port=5001, debug=True)