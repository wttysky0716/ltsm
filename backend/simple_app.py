import os
import sys
import time
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   filename='backend_debug.log')
logger = logging.getLogger(__name__)

from flask import Flask, jsonify, request
from flask_cors import CORS

# 打印调试信息
logger.debug("开始导入模块")
print("正在启动后端服务...")

# 添加当前目录到系统路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 尝试导入数据生成器
try:
    from data_generator import DataGenerator
    from dashboard_controller import DashboardController
    data_available = True
    logger.debug("成功导入数据生成器")
    print("成功导入数据生成器")
except ImportError as e:
    data_available = False
    logger.error(f"无法导入数据生成器: {e}")
    print(f"无法导入数据生成器: {e}")

# 创建一个简单的Flask应用
app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 如果可以导入数据生成器，则创建控制器
if data_available:
    try:
        dashboard_controller = DashboardController(update_interval=30)
        logger.debug("成功创建仪表盘控制器")
        print("成功创建仪表盘控制器")
    except Exception as e:
        logger.error(f"创建仪表盘控制器失败: {e}")
        print(f"创建仪表盘控制器失败: {e}")
        data_available = False

# 添加测试端点
@app.route('/api/test')
def test():
    logger.debug("收到测试请求")
    print("收到测试请求")
    return jsonify({"status": "ok", "message": "Simple backend is running!"})

# 如果数据可用，添加仪表盘数据端点
if data_available:
    @app.route('/api/dashboard-data')
    def get_dashboard_data():
        """获取仪表盘数据API，支持动态更新"""
        logger.debug("收到仪表盘数据请求")
        print("收到仪表盘数据请求")
        try:
            # 获取仪表盘数据
            dashboard_data = dashboard_controller.get_dashboard_data()
            
            # 获取历史数据
            historical_data = dashboard_controller.get_historical_data(days=7)
            
            # 组合数据
            response_data = dashboard_data.copy()
            response_data['historical_data'] = historical_data
            
            logger.debug("成功生成仪表盘数据")
            print("成功生成仪表盘数据")
            return jsonify(response_data)
        except Exception as e:
            logger.error(f"生成仪表盘数据出错: {e}")
            print(f"生成仪表盘数据出错: {e}")
            return jsonify({"error": str(e)}), 500

# 添加模拟登录接口
@app.route('/api/auth/login', methods=['POST'])
def login():
    logger.debug("收到登录请求")
    print("收到登录请求")
    # 简单模拟登录成功
    return jsonify({
        "success": True,
        "token": "mock_token_12345",
        "user": {
            "id": 1,
            "username": "admin",
            "role": "administrator"
        }
    })

# 直接运行测试
logger.debug("准备启动Flask应用，监听端口: 5001")
print("准备启动Flask应用，监听端口: 5001")

# 启动应用
if __name__ == '__main__':
    print("启动Flask应用...")
    app.run(host='0.0.0.0', port=5001, debug=True) 