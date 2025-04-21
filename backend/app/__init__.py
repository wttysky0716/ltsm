import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import config
from .models import db, bcrypt
import logging

# 配置全局日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

jwt = JWTManager()

def create_app(config_name='default'):
    """创建Flask应用实例"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # 初始化扩展
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # 添加JWT错误处理
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        logger.warning(f"令牌已过期: {jwt_payload}")
        return jsonify({"message": "令牌已过期，请重新登录", "error": "token_expired"}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        logger.warning(f"令牌无效: {error}")
        return jsonify({"message": "无效的认证令牌", "error": "invalid_token"}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        logger.warning(f"缺少令牌: {error}")
        return jsonify({"message": "缺少认证令牌", "error": "missing_token"}), 401
    
    @jwt.token_verification_failed_loader
    def verification_failed_callback():
        logger.warning("令牌验证失败")
        return jsonify({"message": "令牌验证失败", "error": "verification_failed"}), 401
    
    # 注册蓝图
    from .routes.auth import auth_bp
    from .routes.logs import logs_bp
    from .routes.analysis import analysis_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(logs_bp, url_prefix='/api/logs')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app
