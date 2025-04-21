import os
from app import create_app

# 获取配置模式
config_name = os.environ.get('FLASK_CONFIG') or 'development'

# 创建应用实例
app = create_app(config_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False) 