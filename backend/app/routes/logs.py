import os
import uuid
import logging
import traceback
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, LogFile

logs_bp = Blueprint('logs', __name__)

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs_api.log')
    ]
)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    """检查文件扩展名是否允许上传"""
    if '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    allowed = extension in current_app.config['ALLOWED_EXTENSIONS']
    logger.debug(f"Checking file extension: {extension}, allowed: {allowed}")
    return allowed

def ensure_upload_folder():
    """确保上传目录存在"""
    upload_folder = current_app.config['UPLOAD_FOLDER']
    logger.debug(f"Checking upload folder: {upload_folder}")
    if not os.path.exists(upload_folder):
        try:
            os.makedirs(upload_folder)
            logger.info(f"Created upload directory: {upload_folder}")
        except Exception as e:
            logger.error(f"Failed to create upload directory: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    # 测试写入权限
    try:
        test_file = os.path.join(upload_folder, 'test_write.tmp')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        logger.debug(f"Upload directory {upload_folder} is writable")
    except Exception as e:
        logger.error(f"Upload directory {upload_folder} is not writable: {str(e)}")
        logger.error(traceback.format_exc())

@logs_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_log():
    """上传日志文件"""
    try:
        logger.info("Starting file upload process")
        logger.debug(f"Request files: {request.files}")
        logger.debug(f"Request form: {request.form}")
        
        # 确保上传目录存在
        ensure_upload_folder()
        
        # 检查是否有文件
        if 'file' not in request.files:
            logger.warning("No file part in request")
            return jsonify({
                'message': '未找到文件',
                'detail': 'request.files中没有file字段'
            }), 400
        
        file = request.files['file']
        logger.info(f"Received file: {file.filename}")
        
        # 检查文件名
        if file.filename == '':
            logger.warning("No selected file")
            return jsonify({
                'message': '未选择文件',
                'detail': '文件名为空'
            }), 400
        
        # 检查文件类型
        if not allowed_file(file.filename):
            logger.warning(f"Invalid file type: {file.filename}")
            return jsonify({
                'message': '不支持的文件类型',
                'detail': f'文件类型必须是: {current_app.config["ALLOWED_EXTENSIONS"]}'
            }), 400
        
        # 安全处理文件名
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
        
        # 生成唯一文件名
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}" if file_extension else f"{uuid.uuid4().hex}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        
        logger.info(f"Saving file to: {filepath}")
        
        try:
            # 保存文件
            file.save(filepath)
            logger.info(f"File saved successfully at: {filepath}")
            
            # 获取文件大小
            file_size = os.path.getsize(filepath)
            logger.debug(f"File size: {file_size} bytes")
            
            # 获取用户ID
            user_id = get_jwt_identity()
            logger.debug(f"User ID: {user_id}")
            
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
            logger.info(f"Database record created for file: {log_file.id}")
            
            return jsonify({
                'message': '文件上传成功',
                'file_id': log_file.id,
                'file': log_file.to_dict()
            }), 201
            
        except Exception as e:
            # 如果保存文件时出错，尝试删除已保存的文件
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    logger.info(f"Cleaned up file after error: {filepath}")
                except Exception as del_e:
                    logger.error(f"Failed to delete file after error: {str(del_e)}")
                    logger.error(traceback.format_exc())
            
            logger.error(f"Error saving file: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'message': '保存文件失败',
                'detail': str(e)
            }), 500
            
    except Exception as e:
        logger.error(f"Unexpected error in upload: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'message': '上传过程中出错',
            'detail': str(e)
        }), 500


@logs_bp.route('/list', methods=['GET'])
@jwt_required()
def list_logs():
    """获取用户的日志文件列表"""
    try:
        user_id = get_jwt_identity()
        logger.debug(f"Fetching log files for user: {user_id}")
        
        # 分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 查询用户的日志文件
        pagination = LogFile.query.filter_by(user_id=user_id).order_by(
            LogFile.upload_time.desc()
        ).paginate(page=page, per_page=per_page)
        
        log_files = pagination.items
        logger.debug(f"Found {len(log_files)} files for user {user_id}")
        
        return jsonify({
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page,
            'files': [log_file.to_dict() for log_file in log_files]
        }), 200
    except Exception as e:
        logger.error(f"Error listing log files: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'message': '获取文件列表失败',
            'detail': str(e)
        }), 500


@logs_bp.route('/<int:file_id>', methods=['GET'])
@jwt_required()
def get_log_file(file_id):
    """获取单个日志文件信息"""
    user_id = get_jwt_identity()
    
    log_file = LogFile.query.filter_by(id=file_id, user_id=user_id).first()
    
    if not log_file:
        return jsonify({'message': '文件不存在或无权访问'}), 404
    
    return jsonify(log_file.to_dict()), 200


@logs_bp.route('/<int:file_id>/download', methods=['GET'])
@jwt_required()
def download_log_file(file_id):
    """下载日志文件"""
    user_id = get_jwt_identity()
    
    log_file = LogFile.query.filter_by(id=file_id, user_id=user_id).first()
    
    if not log_file:
        return jsonify({'message': '文件不存在或无权访问'}), 404
    
    return send_from_directory(current_app.config['UPLOAD_FOLDER'],
                               log_file.filename,
                               as_attachment=True,
                               download_name=log_file.original_filename)


@logs_bp.route('/<int:file_id>', methods=['DELETE'])
@jwt_required()
def delete_log_file(file_id):
    """删除日志文件"""
    user_id = get_jwt_identity()
    
    log_file = LogFile.query.filter_by(id=file_id, user_id=user_id).first()
    
    if not log_file:
        return jsonify({'message': '文件不存在或无权访问'}), 404
    
    # 删除物理文件
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], log_file.filename)
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
    
    user_id = get_jwt_identity()
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