import os
import json
import threading
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db, LogFile, LogAnalysisResult
from ..analyzers.log_analyzer import analyze_log_file

analysis_bp = Blueprint('analysis', __name__)

def process_log_file_async(file_id, user_id):
    """异步处理日志文件"""
    # 获取当前应用实例
    from flask import current_app
    app = current_app._get_current_object()  # 获取实际的应用实例，而不是代理对象
    
    # 使用应用上下文
    with app.app_context():
        # 获取日志文件
        log_file = LogFile.query.filter_by(id=file_id, user_id=user_id).first()
        
        if not log_file:
            return
        
        # 更新状态为处理中
        log_file.status = 'processing'
        log_file.processing_progress = 0.0
        db.session.commit()
        
        try:
            # 获取文件路径
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], log_file.filename)
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                log_file.status = 'failed'
                log_file.processing_progress = 0.0
                db.session.commit()
                return
            
            # 更新进度
            log_file.processing_progress = 10.0
            db.session.commit()
            
            # 分析日志文件
            results = analyze_log_file(file_path)
            
            # 更新进度
            log_file.processing_progress = 80.0
            db.session.commit()
            
            # 检查分析结果是否有错误
            if 'error' in results:
                log_file.status = 'failed'
                log_file.processing_progress = 0.0
                db.session.commit()
                return
            
            # 保存分析结果
            for analysis_type, result_data in results.items():
                if result_data:  # 确保结果不为空
                    analysis_result = LogAnalysisResult(
                        log_file_id=file_id,
                        analysis_type=analysis_type,
                        result_data=json.dumps(result_data)
                    )
                    db.session.add(analysis_result)
            
            # 更新状态为完成
            log_file.status = 'completed'
            log_file.processing_progress = 100.0
            db.session.commit()
            
        except Exception as e:
            print(f"Error processing log file {file_id}: {str(e)}")
            log_file.status = 'failed'
            log_file.processing_progress = 0.0
            db.session.commit()


@analysis_bp.route('/analyze/<int:file_id>', methods=['POST'])
@jwt_required()
def analyze_log(file_id):
    """开始分析日志文件"""
    user_id = get_jwt_identity()
    
    # 检查文件是否存在
    log_file = LogFile.query.filter_by(id=file_id, user_id=user_id).first()
    
    if not log_file:
        return jsonify({'message': '文件不存在或无权访问'}), 404
    
    # 检查文件状态
    if log_file.status == 'processing':
        return jsonify({
            'message': '文件正在处理中',
            'file': log_file.to_dict()
        }), 409
    
    # 启动异步处理
    app = current_app._get_current_object()  # 获取真实的app对象而不是代理
    thread = threading.Thread(target=process_log_file_async, args=(file_id, user_id))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'message': '已开始分析日志文件',
        'file': log_file.to_dict()
    }), 202


@analysis_bp.route('/results/<int:file_id>', methods=['GET'])
@jwt_required()
def get_analysis_results(file_id):
    """获取日志文件的分析结果"""
    user_id = get_jwt_identity()
    
    # 检查文件是否存在
    log_file = LogFile.query.filter_by(id=file_id, user_id=user_id).first()
    
    if not log_file:
        return jsonify({'message': '文件不存在或无权访问'}), 404
    
    # 获取分析结果
    analysis_results = LogAnalysisResult.query.filter_by(log_file_id=file_id).all()
    
    if not analysis_results:
        return jsonify({
            'message': '尚无分析结果',
            'file_status': log_file.status,
            'processing_progress': log_file.processing_progress
        }), 404
    
    # 将结果整理为字典
    results = {}
    for result in analysis_results:
        results[result.analysis_type] = json.loads(result.result_data)
    
    return jsonify({
        'file': log_file.to_dict(),
        'results': results
    }), 200


@analysis_bp.route('/results/<int:file_id>/<analysis_type>', methods=['GET'])
@jwt_required()
def get_specific_analysis_result(file_id, analysis_type):
    """获取特定类型的分析结果"""
    user_id = get_jwt_identity()
    
    # 检查文件是否存在
    log_file = LogFile.query.filter_by(id=file_id, user_id=user_id).first()
    
    if not log_file:
        return jsonify({'message': '文件不存在或无权访问'}), 404
    
    # 获取特定类型的分析结果
    analysis_result = LogAnalysisResult.query.filter_by(
        log_file_id=file_id,
        analysis_type=analysis_type
    ).first()
    
    if not analysis_result:
        return jsonify({
            'message': f'没有找到类型为 {analysis_type} 的分析结果',
            'file_status': log_file.status,
            'processing_progress': log_file.processing_progress
        }), 404
    
    return jsonify({
        'file': log_file.to_dict(),
        'analysis_type': analysis_type,
        'result': json.loads(analysis_result.result_data)
    }), 200 