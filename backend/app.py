import os
from app import create_app
from flask import jsonify
from flask_cors import CORS

# 获取配置模式
config_name = os.environ.get('FLASK_CONFIG') or 'development'

# 创建应用实例
app = create_app(config_name)
CORS(app)  # 启用所有域的跨域支持

# 添加一个简单的测试端点
@app.route('/api/test')
def test():
    return jsonify({"status": "ok", "message": "Backend is running!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # 启用调试模式 