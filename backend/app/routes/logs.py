import os
import uuid
import logging
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, LogFile

logs_bp = Blueprint('logs', __name__)

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    """检查文件扩展名是否允许上传"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def ensure_upload_folder():
    """确保上传目录存在"""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    # 确保是绝对路径
    upload_folder = os.path.abspath(upload_folder)
    
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    return upload_folder

@logs_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_log():
    """上传日志文件"""
    try:
        logger.info("开始文件上传处理")
        
        # 确保上传目录存在
        upload_folder = ensure_upload_folder()
        
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({'message': '未找到文件'}), 400
        
        file = request.files['file']
        
        # 检查文件名
        if file.filename == '':
            return jsonify({'message': '未选择文件'}), 400
        
        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify({'message': '不支持的文件类型'}), 400
        
        # 安全处理文件名
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
        
        # 生成唯一文件名
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}" if file_extension else f"{uuid.uuid4().hex}"
        filepath = os.path.join(upload_folder, unique_filename)
        
        # 保存文件
        file.save(filepath)
        
        # 获取文件大小
        file_size = os.path.getsize(filepath)
        
        # 获取用户ID
        user_id = int(get_jwt_identity())
        
        # 创建数据库记录
        log_file = LogFile(
            filename=unique_filename,
            original_filename=original_filename,
            file_size=file_size,
            file_type=file_extension,
            user_id=user_id,
            status='uploaded'
        )
        
        db.session.add(log_file)
        db.session.commit()
        
        logger.info(f"文件上传成功: {original_filename}")
        
        return jsonify({
            'message': '文件上传成功',
            'file_id': log_file.id,
            'file': log_file.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        return jsonify({'message': f'上传过程中出错: {str(e)}'}), 500

@logs_bp.route('/list', methods=['GET'])
@jwt_required()
def list_logs():
    """获取用户的日志文件列表"""
    try:
        user_id = int(get_jwt_identity())
        
        # 分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 查询用户的日志文件
        pagination = LogFile.query.filter_by(user_id=user_id).order_by(
            LogFile.upload_time.desc()
        ).paginate(page=page, per_page=per_page)
        
        log_files = pagination.items
        
        return jsonify({
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page,
            'files': [log_file.to_dict() for log_file in log_files]
        }), 200
    except Exception as e:
        logger.error(f"获取文件列表失败: {str(e)}")
        return jsonify({'message': f'获取文件列表失败: {str(e)}'}), 500

@logs_bp.route('/<int:file_id>', methods=['GET'])
@jwt_required()
def get_log_file(file_id):
    """获取单个日志文件信息"""
    user_id = int(get_jwt_identity())
    
    log_file = LogFile.query.filter_by(id=file_id, user_id=user_id).first()
    
    if not log_file:
        return jsonify({'message': '文件不存在或无权访问'}), 404
    
    return jsonify(log_file.to_dict()), 200

@logs_bp.route('/<int:file_id>/download', methods=['GET'])
@jwt_required()
def download_log_file(file_id):
    """下载日志文件"""
    user_id = int(get_jwt_identity())
    
    log_file = LogFile.query.filter_by(id=file_id, user_id=user_id).first()
    
    if not log_file:
        return jsonify({'message': '文件不存在或无权访问'}), 404
    
    upload_folder = os.path.abspath(current_app.config['UPLOAD_FOLDER'])
    return send_from_directory(upload_folder,
                               log_file.filename,
                               as_attachment=True,
                               download_name=log_file.original_filename)

@logs_bp.route('/<int:file_id>', methods=['DELETE'])
@jwt_required()
def delete_log_file(file_id):
    """删除日志文件"""
    user_id = int(get_jwt_identity())
    
    log_file = LogFile.query.filter_by(id=file_id, user_id=user_id).first()
    
    if not log_file:
        return jsonify({'message': '文件不存在或无权访问'}), 404
    
    # 删除物理文件
    upload_folder = os.path.abspath(current_app.config['UPLOAD_FOLDER'])
    file_path = os.path.join(upload_folder, log_file.filename)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        return jsonify({'message': f'删除文件失败: {str(e)}'}), 500
    
    # 删除数据库记录
    db.session.delete(log_file)
    db.session.commit()
    
    return jsonify({'message': '文件删除成功'}), 200

@logs_bp.route('/<int:file_id>/progress', methods=['PUT'])
@jwt_required()
def update_progress(file_id):
    """更新日志文件处理进度"""
    data = request.get_json()
    
    if not data or 'progress' not in data or 'status' not in data:
        return jsonify({'message': '缺少必要参数'}), 400
    
    user_id = int(get_jwt_identity())
    log_file = LogFile.query.filter_by(id=file_id).first()
    
    if not log_file:
        return jsonify({'message': '文件不存在'}), 404
    
    # 更新进度和状态
    log_file.processing_progress = float(data['progress'])
    log_file.status = data['status']
    
    db.session.commit()
    
    return jsonify({
        'message': '进度更新成功',
        'file': log_file.to_dict()
    }), 200 