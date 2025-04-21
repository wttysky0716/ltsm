from datetime import datetime
from .user import db

class LogFile(db.Model):
    """日志文件模型"""
    __tablename__ = 'log_files'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # 文件大小（字节）
    file_type = db.Column(db.String(50))
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    processing_progress = db.Column(db.Float, default=0.0)  # 处理进度 0-100
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # 关系
    user = db.relationship('User', backref=db.backref('log_files', lazy='dynamic'))
    
    def __init__(self, filename, original_filename, file_size, file_type, user_id, status='pending'):
        self.filename = filename
        self.original_filename = original_filename
        self.file_size = file_size
        self.file_type = file_type
        self.user_id = user_id
        self.status = status
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'upload_time': self.upload_time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': self.status,
            'processing_progress': self.processing_progress,
            'user_id': self.user_id
        }
    
    def __repr__(self):
        return f'<LogFile {self.original_filename}>'


class LogAnalysisResult(db.Model):
    """日志分析结果模型"""
    __tablename__ = 'log_analysis_results'
    
    id = db.Column(db.Integer, primary_key=True)
    log_file_id = db.Column(db.Integer, db.ForeignKey('log_files.id'))
    analysis_type = db.Column(db.String(50))  # 'anomaly', 'trend', 'summary'
    result_data = db.Column(db.Text)  # JSON格式的分析结果
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    log_file = db.relationship('LogFile', backref=db.backref('analysis_results', lazy='dynamic'))
    
    def __init__(self, log_file_id, analysis_type, result_data):
        self.log_file_id = log_file_id
        self.analysis_type = analysis_type
        self.result_data = result_data
    
    def to_dict(self):
        return {
            'id': self.id,
            'log_file_id': self.log_file_id,
            'analysis_type': self.analysis_type,
            'result_data': self.result_data,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def __repr__(self):
        return f'<LogAnalysisResult {self.id} {self.analysis_type}>' 