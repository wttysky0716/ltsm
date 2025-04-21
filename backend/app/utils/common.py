import os
import re
import uuid
import json
from datetime import datetime
from functools import wraps
from flask import jsonify, current_app, request
from werkzeug.utils import secure_filename

def allowed_file(filename, allowed_extensions=None):
    """检查文件扩展名是否允许上传"""
    if allowed_extensions is None:
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', set())
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_unique_filename(original_filename):
    """生成唯一文件名"""
    # 安全处理文件名
    safe_filename = secure_filename(original_filename)
    file_extension = safe_filename.rsplit('.', 1)[1].lower() if '.' in safe_filename else ''
    
    # 生成唯一文件名
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}" if file_extension else f"{uuid.uuid4().hex}"
    
    return unique_filename, file_extension

def save_file(file, upload_folder=None):
    """保存上传的文件并返回文件信息"""
    if upload_folder is None:
        upload_folder = current_app.config.get('UPLOAD_FOLDER')
    
    # 生成唯一文件名
    unique_filename, file_extension = generate_unique_filename(file.filename)
    
    # 确保上传目录存在
    os.makedirs(upload_folder, exist_ok=True)
    
    # 构建完整的文件路径
    filepath = os.path.join(upload_folder, unique_filename)
    
    # 保存文件
    file.save(filepath)
    
    # 获取文件大小
    file_size = os.path.getsize(filepath)
    
    return {
        'filename': unique_filename,
        'original_filename': file.filename,
        'file_size': file_size,
        'file_type': file_extension,
        'filepath': filepath
    }

def format_datetime(dt, format_str='%Y-%m-%d %H:%M:%S'):
    """格式化日期时间对象为字符串"""
    if isinstance(dt, datetime):
        return dt.strftime(format_str)
    return dt

def parse_datetime(dt_str, format_str='%Y-%m-%d %H:%M:%S'):
    """将字符串解析为日期时间对象"""
    try:
        return datetime.strptime(dt_str, format_str)
    except (ValueError, TypeError):
        return None

def json_dumps(data):
    """将数据序列化为JSON字符串，处理datetime等特殊类型"""
    def _json_serial(obj):
        """JSON序列化特殊对象"""
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        raise TypeError(f"Type {type(obj)} not serializable")
    
    return json.dumps(data, default=_json_serial)

def json_response(data, status=200):
    """生成JSON响应"""
    return jsonify(data), status

def extract_log_datetime(log_line):
    """从日志行中提取日期时间"""
    # 通用的日期时间模式匹配
    patterns = [
        # 标准的syslog格式: Jan 1 12:34:56
        r'(\w{3}\s+\d{1,2}\s+\d{1,2}:\d{1,2}:\d{1,2})',
        # 包含年份的格式: 2023-01-01 12:34:56
        r'(\d{4}-\d{1,2}-\d{1,2}\s+\d{1,2}:\d{1,2}:\d{1,2})',
        # ISO格式: 2023-01-01T12:34:56
        r'(\d{4}-\d{1,2}-\d{1,2}T\d{1,2}:\d{1,2}:\d{1,2})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, log_line)
        if match:
            date_str = match.group(1)
            try:
                # 尝试各种格式解析
                format_strs = [
                    '%b %d %H:%M:%S',  # 标准syslog
                    '%Y-%m-%d %H:%M:%S',  # 标准时间戳
                    '%Y-%m-%dT%H:%M:%S'  # ISO格式
                ]
                
                for fmt in format_strs:
                    try:
                        # 如果没有年份，添加当前年份
                        if '%Y' not in fmt and date_str:
                            current_year = datetime.now().year
                            date_obj = datetime.strptime(f"{current_year} {date_str}", f"%Y {fmt}")
                        else:
                            date_obj = datetime.strptime(date_str, fmt)
                        return date_obj
                    except ValueError:
                        continue
            except Exception:
                pass
    
    return None 