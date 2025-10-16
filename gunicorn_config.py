# gunicorn_config.py
def post_worker_init(worker):
    """工作进程初始化后执行"""
    from run_app import app, init_app
    
    # 在应用上下文中执行初始化
    with app.app_context():
        print("⚡ 工作进程初始化中...")
        init_app()

