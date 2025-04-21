import re
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter
import os
import random

class LogAnalyzer:
    """日志分析器基类"""
    
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path
        self.log_data = None
        self.results = {
            'summary': {},
            'anomalies': [],
            'trends': {}
        }
    
    def read_log_file(self):
        """读取日志文件，由子类实现具体逻辑"""
        raise NotImplementedError("子类必须实现该方法")
    
    def analyze(self):
        """分析日志文件"""
        self.read_log_file()
        self.generate_summary()
        self.detect_anomalies()
        self.analyze_trends()
        return self.results
    
    def generate_summary(self):
        """生成日志摘要统计信息"""
        raise NotImplementedError("子类必须实现该方法")
    
    def detect_anomalies(self):
        """检测异常情况"""
        raise NotImplementedError("子类必须实现该方法")
    
    def analyze_trends(self):
        """分析趋势"""
        raise NotImplementedError("子类必须实现该方法")


class AuthLogAnalyzer(LogAnalyzer):
    """认证日志分析器"""
    
    def __init__(self, log_file_path):
        super().__init__(log_file_path)
        self.log_entries = []
        self.auth_events = []
    
    def read_log_file(self):
        """读取认证日志文件"""
        patterns = [
            # Linux标准认证日志格式
            r'(\w{3}\s+\d+\s+\d+:\d+:\d+)\s+(\S+)\s+(\S+)(?:\[(\d+)\])?:\s+(.+)',
            # Windows事件日志格式
            r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(\S+)\s+(\S+)\s+(\d+)\s+(.+)',
            # 通用格式
            r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)\s+(\S+)\s+(\S+)(?:\[(\d+)\])?:\s+(.+)'
        ]
        
        with open(self.log_file_path, 'r', errors='ignore') as f:
            for line in f:
                matched = False
                line = line.strip()
                
                # 尝试所有模式
                for pattern in patterns:
                    match = re.match(pattern, line)
                    if match:
                        matched = True
                        timestamp_str, hostname, service, pid, message = match.groups()
                        try:
                            # 根据不同格式解析时间戳
                            if 'T' in timestamp_str:  # ISO格式
                                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            elif '-' in timestamp_str:  # YYYY-MM-DD格式
                                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                            else:  # MMM DD HH:MM:SS格式
                                current_year = datetime.now().year
                                timestamp = datetime.strptime(f"{current_year} {timestamp_str}", "%Y %b %d %H:%M:%S")
                            
                            entry = {
                                'timestamp': timestamp,
                                'hostname': hostname,
                                'service': service,
                                'pid': pid,
                                'message': message
                            }
                            self.log_entries.append(entry)
                            
                            # 提取认证事件 - 增强识别能力
                            if self._is_auth_event(service, message):
                                auth_event = self._parse_auth_event(timestamp, service, message)
                                if auth_event:
                                    self.auth_events.append(auth_event)
                        except Exception as e:
                            print(f"Error parsing log entry: {line} - {str(e)}")
                            continue
                        break  # 匹配成功则跳出循环
                
                # JSON格式处理
                if not matched and line.startswith('{') and line.endswith('}'):
                    try:
                        json_entry = json.loads(line)
                        if self._is_valid_json_log(json_entry):
                            self._process_json_log(json_entry)
                    except json.JSONDecodeError:
                        pass
    
    def _is_valid_json_log(self, json_entry):
        """检查JSON日志是否包含必要字段"""
        required_fields = ['timestamp', 'message']
        return all(field in json_entry for field in required_fields)
    
    def _process_json_log(self, json_entry):
        """处理JSON格式的日志"""
        try:
            # 尝试不同的时间戳格式
            timestamp = None
            timestamp_str = json_entry['timestamp']
            
            try:
                if 'T' in timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                # 如果无法解析，使用当前时间
                timestamp = datetime.now()
            
            hostname = json_entry.get('hostname', 'unknown')
            service = json_entry.get('service', json_entry.get('logger', 'unknown'))
            pid = json_entry.get('pid', json_entry.get('process_id', None))
            message = json_entry['message']
            
            entry = {
                'timestamp': timestamp,
                'hostname': hostname,
                'service': service,
                'pid': pid,
                'message': message
            }
            self.log_entries.append(entry)
            
            # 检查是否为认证事件
            if self._is_auth_event(service, message):
                auth_event = self._parse_auth_event(timestamp, service, message)
                if auth_event:
                    self.auth_events.append(auth_event)
        except Exception as e:
            print(f"Error processing JSON log: {str(e)}")
    
    def _is_auth_event(self, service, message):
        """检查是否为认证事件"""
        auth_services = ['sshd', 'login', 'su', 'sudo', 'auth', 'security']
        auth_keywords = ['login', 'password', 'authentication', 'session', 'user', 'failed', 'success']
        
        if any(auth_service in service.lower() for auth_service in auth_services):
            return True
        
        return any(keyword in message.lower() for keyword in auth_keywords)
    
    def _parse_auth_event(self, timestamp, service, message):
        """解析认证事件信息"""
        # 尝试提取用户和IP
        user_match = re.search(r'(?:user|for|account)\s+(\S+)', message, re.IGNORECASE)
        ip_match = re.search(r'(?:from|source)\s+(\d+\.\d+\.\d+\.\d+)', message, re.IGNORECASE)
        
        # 确定事件类型
        event_type = 'failure'
        if any(word in message.lower() for word in ['accepted', 'success', 'successful', 'opened']):
            event_type = 'success'
        
        user = user_match.group(1) if user_match else 'unknown'
        source_ip = ip_match.group(1) if ip_match else 'unknown'
        
        return {
            'timestamp': timestamp,
            'type': event_type,
            'user': user,
            'source_ip': source_ip,
            'message': message
        }
    
    def generate_summary(self):
        """生成认证日志摘要统计信息"""
        if not self.log_entries:
            self.results['summary'] = {
                'total_entries': 0,
                'error': '无有效日志条目'
            }
            return
        
        # 计算认证成功和失败次数
        success_count = sum(1 for event in self.auth_events if event['type'] == 'success')
        failure_count = sum(1 for event in self.auth_events if event['type'] == 'failure')
        
        # 按用户统计登录尝试
        user_attempts = {}
        for event in self.auth_events:
            user = event['user']
            if user not in user_attempts:
                user_attempts[user] = {'success': 0, 'failure': 0}
            
            if event['type'] == 'success':
                user_attempts[user]['success'] += 1
            else:
                user_attempts[user]['failure'] += 1
        
        # 按IP地址统计登录尝试
        ip_attempts = {}
        for event in self.auth_events:
            ip = event['source_ip']
            if ip != 'unknown':
                if ip not in ip_attempts:
                    ip_attempts[ip] = {'success': 0, 'failure': 0}
                
                if event['type'] == 'success':
                    ip_attempts[ip]['success'] += 1
                else:
                    ip_attempts[ip]['failure'] += 1
        
        # 统计每小时登录尝试次数
        hourly_attempts = {}
        for event in self.auth_events:
            hour = event['timestamp'].hour
            if hour not in hourly_attempts:
                hourly_attempts[hour] = {'success': 0, 'failure': 0}
            
            if event['type'] == 'success':
                hourly_attempts[hour]['success'] += 1
            else:
                hourly_attempts[hour]['failure'] += 1
        
        # 格式化为按小时排序的列表
        hourly_data = []
        for hour in range(24):
            if hour in hourly_attempts:
                hourly_data.append({
                    'hour': hour,
                    'success': hourly_attempts[hour]['success'],
                    'failure': hourly_attempts[hour]['failure'],
                    'total': hourly_attempts[hour]['success'] + hourly_attempts[hour]['failure']
                })
            else:
                hourly_data.append({
                    'hour': hour,
                    'success': 0,
                    'failure': 0,
                    'total': 0
                })
        
        self.results['summary'] = {
            'total_entries': len(self.log_entries),
            'auth_events': len(self.auth_events),
            'success_count': success_count,
            'failure_count': failure_count,
            'success_rate': (success_count / len(self.auth_events)) * 100 if self.auth_events else 0,
            'user_attempts': user_attempts,
            'ip_attempts': ip_attempts,
            'hourly_attempts': hourly_data,
            'log_start_time': min(entry['timestamp'] for entry in self.log_entries).strftime('%Y-%m-%d %H:%M:%S'),
            'log_end_time': max(entry['timestamp'] for entry in self.log_entries).strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def detect_anomalies(self):
        """检测认证日志异常情况"""
        if not self.auth_events:
            return
        
        # 1. 检测登录失败异常
        # 对于每个用户，如果失败次数超过成功次数的3倍，标记为异常
        for user, attempts in self.results['summary']['user_attempts'].items():
            if attempts['failure'] > 3 and attempts['failure'] > attempts['success'] * 3:
                self.results['anomalies'].append({
                    'type': 'user_high_failure',
                    'user': user,
                    'failure_count': attempts['failure'],
                    'success_count': attempts['success'],
                    'severity': 'high' if attempts['failure'] > 10 else 'medium',
                    'description': f"用户 {user} 登录失败次数({attempts['failure']})显著高于成功次数({attempts['success']})"
                })
        
        # 2. 检测来自单个IP的大量失败
        for ip, attempts in self.results['summary']['ip_attempts'].items():
            if attempts['failure'] > 5:
                self.results['anomalies'].append({
                    'type': 'ip_high_failure',
                    'ip': ip,
                    'failure_count': attempts['failure'],
                    'success_count': attempts['success'],
                    'severity': 'high' if attempts['failure'] > 20 else 'medium',
                    'description': f"IP地址 {ip} 有大量登录失败尝试({attempts['failure']}次)"
                })
        
        # 3. 检测异常登录时间（如果在凌晨0-5点有大量登录）
        for hour_data in self.results['summary']['hourly_attempts']:
            hour = hour_data['hour']
            if 0 <= hour <= 5 and hour_data['total'] > 5:
                self.results['anomalies'].append({
                    'type': 'unusual_login_time',
                    'hour': hour,
                    'attempt_count': hour_data['total'],
                    'severity': 'medium',
                    'description': f"在非常规时间(凌晨{hour}点)有大量({hour_data['total']}次)登录尝试"
                })
        
        # 4. 新增：检测短时间内的爆破尝试
        if len(self.auth_events) > 10:
            # 按时间排序
            sorted_events = sorted(self.auth_events, key=lambda x: x['timestamp'])
            # 检查是否存在短时间内大量失败尝试
            failed_counts = []
            for i in range(len(sorted_events) - 5):  # 检查每5个连续事件
                window = sorted_events[i:i+5]
                if sum(1 for e in window if e['type'] == 'failure') >= 4:  # 至少4个失败
                    # 检查时间窗口是否小于5分钟
                    time_diff = (window[-1]['timestamp'] - window[0]['timestamp']).total_seconds()
                    if time_diff < 300:  # 5分钟 = 300秒
                        failed_counts.append({
                            'start_time': window[0]['timestamp'],
                            'end_time': window[-1]['timestamp'],
                            'count': sum(1 for e in window if e['type'] == 'failure'),
                            'time_span': time_diff
                        })
            
            # 合并相邻的爆破尝试
            if failed_counts:
                # 只保留最严重的一次爆破尝试
                worst_attempt = max(failed_counts, key=lambda x: x['count'])
                self.results['anomalies'].append({
                    'type': 'brute_force_attempt',
                    'start_time': worst_attempt['start_time'].strftime('%Y-%m-%d %H:%M:%S'),
                    'end_time': worst_attempt['end_time'].strftime('%Y-%m-%d %H:%M:%S'),
                    'failure_count': worst_attempt['count'],
                    'time_span_seconds': worst_attempt['time_span'],
                    'severity': 'high',
                    'description': f"检测到可能的暴力破解尝试，在{worst_attempt['time_span']:.1f}秒内有{worst_attempt['count']}次失败尝试"
                })
    
    def analyze_trends(self):
        """分析认证日志趋势"""
        if not self.auth_events:
            return
        
        # 提取最近的趋势（按日期分组）
        daily_attempts = {}
        for event in self.auth_events:
            date_str = event['timestamp'].strftime('%Y-%m-%d')
            if date_str not in daily_attempts:
                daily_attempts[date_str] = {'success': 0, 'failure': 0}
            
            if event['type'] == 'success':
                daily_attempts[date_str]['success'] += 1
            else:
                daily_attempts[date_str]['failure'] += 1
        
        # 转换为按日期排序的列表
        trend_data = []
        for date_str in sorted(daily_attempts.keys()):
            trend_data.append({
                'date': date_str,
                'success': daily_attempts[date_str]['success'],
                'failure': daily_attempts[date_str]['failure'],
                'total': daily_attempts[date_str]['success'] + daily_attempts[date_str]['failure']
            })
        
        # 计算失败率的变化趋势
        if len(trend_data) > 1:
            current_failure_rate = trend_data[-1]['failure'] / trend_data[-1]['total'] if trend_data[-1]['total'] > 0 else 0
            previous_failure_rate = trend_data[-2]['failure'] / trend_data[-2]['total'] if trend_data[-2]['total'] > 0 else 0
            failure_rate_change = current_failure_rate - previous_failure_rate
            
            trend_description = "登录失败率保持稳定"
            if failure_rate_change > 0.1:
                trend_description = "登录失败率显著上升，可能需要关注"
            elif failure_rate_change < -0.1:
                trend_description = "登录失败率显著下降，安全状况改善"
        else:
            trend_description = "数据不足以分析趋势变化"
        
        self.results['trends'] = {
            'daily_attempts': trend_data,
            'trend_description': trend_description
        }


class SystemLogAnalyzer(LogAnalyzer):
    """系统日志分析器"""
    
    def __init__(self, log_file_path):
        super().__init__(log_file_path)
        self.log_entries = []
    
    def read_log_file(self):
        """读取系统日志文件"""
        patterns = [
            # Linux标准系统日志格式
            r'(\w{3}\s+\d+\s+\d+:\d+:\d+)\s+(\S+)\s+(\S+)(?:\[(\d+)\])?:\s+(.+)',
            # Windows事件日志格式
            r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(\S+)\s+(\S+)\s+(\d+)\s+(.+)',
            # 通用格式
            r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)\s+(\S+)\s+(\S+)(?:\[(\d+)\])?:\s+(.+)'
        ]
        
        with open(self.log_file_path, 'r', errors='ignore') as f:
            for line in f:
                matched = False
                line = line.strip()
                
                # 尝试所有模式
                for pattern in patterns:
                    match = re.match(pattern, line)
                    if match:
                        matched = True
                        timestamp_str, hostname, service, pid, message = match.groups()
                        try:
                            # 根据不同格式解析时间戳
                            if 'T' in timestamp_str:  # ISO格式
                                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            elif '-' in timestamp_str:  # YYYY-MM-DD格式
                                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                            else:  # MMM DD HH:MM:SS格式
                                current_year = datetime.now().year
                                timestamp = datetime.strptime(f"{current_year} {timestamp_str}", "%Y %b %d %H:%M:%S")
                            
                            entry = {
                                'timestamp': timestamp,
                                'hostname': hostname,
                                'service': service,
                                'pid': pid,
                                'message': message,
                                'severity': self._determine_severity(message)
                            }
                            self.log_entries.append(entry)
                        except Exception as e:
                            print(f"Error parsing log entry: {line} - {str(e)}")
                            continue
                        break  # 匹配成功则跳出循环
                
                # JSON格式处理
                if not matched and line.startswith('{') and line.endswith('}'):
                    try:
                        json_entry = json.loads(line)
                        if 'timestamp' in json_entry and 'message' in json_entry:
                            self._process_json_log(json_entry)
                    except json.JSONDecodeError:
                        pass
    
    def _process_json_log(self, json_entry):
        """处理JSON格式的日志"""
        try:
            # 尝试不同的时间戳格式
            timestamp = None
            timestamp_str = json_entry['timestamp']
            
            try:
                if 'T' in timestamp_str:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                else:
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                # 如果无法解析，使用当前时间
                timestamp = datetime.now()
            
            hostname = json_entry.get('hostname', 'unknown')
            service = json_entry.get('service', json_entry.get('logger', 'unknown'))
            pid = json_entry.get('pid', json_entry.get('process_id', None))
            message = json_entry['message']
            
            # 确定严重程度 - 首先检查json中是否已包含
            if 'level' in json_entry:
                severity = self._map_log_level(json_entry['level'])
            else:
                severity = self._determine_severity(message)
            
            entry = {
                'timestamp': timestamp,
                'hostname': hostname,
                'service': service,
                'pid': pid,
                'message': message,
                'severity': severity
            }
            self.log_entries.append(entry)
        except Exception as e:
            print(f"Error processing JSON log: {str(e)}")
    
    def _map_log_level(self, level):
        """将各种日志级别映射到标准化的严重程度"""
        level = str(level).lower()
        
        if level in ['error', 'err', 'fatal', 'critical', 'crit', 'alert', 'emerg', 'emergency']:
            return 'error'
        elif level in ['warn', 'warning']:
            return 'warning'
        elif level in ['info', 'information', 'notice', 'debug']:
            return 'info'
        else:
            return 'info'  # 默认值
    
    def _determine_severity(self, message):
        """根据消息内容确定严重性"""
        if any(keyword in message.lower() for keyword in ['error', 'fail', 'critical', 'alert', 'emerg', 'exception', 'crash']):
            return 'error'
        elif any(keyword in message.lower() for keyword in ['warn', 'warning']):
            return 'warning'
        else:
            return 'info'
    
    def generate_summary(self):
        """生成系统日志摘要统计信息"""
        if not self.log_entries:
            self.results['summary'] = {
                'total_entries': 0,
                'error': '无有效日志条目'
            }
            return
        
        # 按服务统计日志数量
        service_counts = Counter(entry['service'] for entry in self.log_entries)
        
        # 按严重程度统计日志数量
        severity_counts = Counter(entry['severity'] for entry in self.log_entries)
        
        # 按小时统计日志数量
        hourly_counts = {}
        for entry in self.log_entries:
            hour = entry['timestamp'].hour
            if hour not in hourly_counts:
                hourly_counts[hour] = {'info': 0, 'warning': 0, 'error': 0}
            
            hourly_counts[hour][entry['severity']] += 1
        
        # 格式化为按小时排序的列表
        hourly_data = []
        for hour in range(24):
            if hour in hourly_counts:
                hourly_data.append({
                    'hour': hour,
                    'info': hourly_counts[hour]['info'],
                    'warning': hourly_counts[hour]['warning'],
                    'error': hourly_counts[hour]['error'],
                    'total': sum(hourly_counts[hour].values())
                })
            else:
                hourly_data.append({
                    'hour': hour,
                    'info': 0,
                    'warning': 0,
                    'error': 0,
                    'total': 0
                })
        
        # 提取最常见的错误消息
        error_entries = [entry for entry in self.log_entries if entry['severity'] == 'error']
        common_errors = Counter(entry['message'] for entry in error_entries).most_common(10)
        
        self.results['summary'] = {
            'total_entries': len(self.log_entries),
            'service_distribution': dict(service_counts),
            'severity_distribution': dict(severity_counts),
            'hourly_distribution': hourly_data,
            'common_errors': [{'message': msg, 'count': count} for msg, count in common_errors],
            'log_start_time': min(entry['timestamp'] for entry in self.log_entries).strftime('%Y-%m-%d %H:%M:%S'),
            'log_end_time': max(entry['timestamp'] for entry in self.log_entries).strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def detect_anomalies(self):
        """检测系统日志异常情况"""
        if not self.log_entries:
            return
        
        # 1. 检测错误日志异常
        error_ratio = self.results['summary']['severity_distribution'].get('error', 0) / len(self.log_entries)
        if error_ratio > 0.2:  # 如果错误日志超过20%
            self.results['anomalies'].append({
                'type': 'high_error_ratio',
                'error_count': self.results['summary']['severity_distribution'].get('error', 0),
                'total_count': len(self.log_entries),
                'error_ratio': error_ratio,
                'severity': 'high' if error_ratio > 0.5 else 'medium',
                'description': f"错误日志比例异常高({error_ratio*100:.1f}%)，可能表明系统存在问题"
            })
        
        # 2. 检测特定服务的错误集中
        service_error_counts = {}
        for entry in self.log_entries:
            if entry['severity'] == 'error':
                service = entry['service']
                service_error_counts[service] = service_error_counts.get(service, 0) + 1
        
        for service, error_count in service_error_counts.items():
            total_service_logs = self.results['summary']['service_distribution'].get(service, 0)
            if error_count > 10 and error_count/total_service_logs > 0.5:
                self.results['anomalies'].append({
                    'type': 'service_high_errors',
                    'service': service,
                    'error_count': error_count,
                    'total_service_logs': total_service_logs,
                    'error_ratio': error_count/total_service_logs,
                    'severity': 'high',
                    'description': f"服务 {service} 的错误日志数量异常高({error_count}条，占该服务日志的{error_count/total_service_logs*100:.1f}%)"
                })
        
        # 3. 使用简单的统计方法检测异常，替代机器学习方法
        if len(self.log_entries) > 100:
            # 对每小时的错误日志数量进行分析
            hourly_error_counts = {}
            for entry in self.log_entries:
                if entry['severity'] == 'error':
                    hour = entry['timestamp'].hour
                    hourly_error_counts[hour] = hourly_error_counts.get(hour, 0) + 1
            
            # 计算错误日志小时分布的平均值和标准差
            if hourly_error_counts:
                hours = list(range(24))
                error_counts = [hourly_error_counts.get(hour, 0) for hour in hours]
                mean_errors = sum(error_counts) / len(hours)
                std_errors = np.std(error_counts) if len(error_counts) > 1 else 0
                
                # 检测错误数量明显高于平均值的小时
                for hour, count in hourly_error_counts.items():
                    if std_errors > 0 and count > mean_errors + 2 * std_errors:  # 超过2个标准差
                        # 找到该小时的一些错误日志作为样本
                        sample_entries = [entry for entry in self.log_entries 
                                         if entry['timestamp'].hour == hour and entry['severity'] == 'error'][:3]
                        
                        if sample_entries:
                            self.results['anomalies'].append({
                                'type': 'time_based_anomaly',
                                'hour': hour,
                                'error_count': count,
                                'avg_errors': mean_errors,
                                'severity': 'medium',
                                'description': f"在{hour}时检测到异常高的错误日志数量({count}条，平均为{mean_errors:.1f}条)"
                            })
    
    def analyze_trends(self):
        """分析系统日志趋势"""
        if not self.log_entries:
            return
        
        # 按日期分组
        daily_counts = {}
        for entry in self.log_entries:
            date_str = entry['timestamp'].strftime('%Y-%m-%d')
            severity = entry['severity']
            
            if date_str not in daily_counts:
                daily_counts[date_str] = {'info': 0, 'warning': 0, 'error': 0}
            
            daily_counts[date_str][severity] += 1
        
        # 转换为按日期排序的列表
        trend_data = []
        for date_str in sorted(daily_counts.keys()):
            trend_data.append({
                'date': date_str,
                'info': daily_counts[date_str]['info'],
                'warning': daily_counts[date_str]['warning'],
                'error': daily_counts[date_str]['error'],
                'total': sum(daily_counts[date_str].values())
            })
        
        # 计算错误率的变化趋势
        if len(trend_data) > 1:
            current_error_rate = trend_data[-1]['error'] / trend_data[-1]['total'] if trend_data[-1]['total'] > 0 else 0
            previous_error_rate = trend_data[-2]['error'] / trend_data[-2]['total'] if trend_data[-2]['total'] > 0 else 0
            error_rate_change = current_error_rate - previous_error_rate
            
            trend_description = "系统错误率保持稳定"
            if error_rate_change > 0.1:
                trend_description = "系统错误率显著上升，需要关注"
            elif error_rate_change < -0.1:
                trend_description = "系统错误率显著下降，系统状况改善"
        else:
            trend_description = "数据不足以分析趋势变化"
        
        self.results['trends'] = {
            'daily_counts': trend_data,
            'trend_description': trend_description
        }


def get_analyzer_for_file(file_path):
    """根据文件内容选择合适的分析器"""
    # 读取文件的前几行来判断类型
    sample_lines = []
    try:
        with open(file_path, 'r', errors='ignore') as f:
            for _ in range(20):  # 增加到前20行以提高判断准确性
                line = f.readline().strip()
                if line:
                    sample_lines.append(line)
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return None
    
    if not sample_lines:
        print(f"File {file_path} is empty or cannot be read")
        return None
    
    # 检查是否为JSON格式日志
    if sample_lines[0].startswith('{') and sample_lines[0].endswith('}'):
        try:
            json_obj = json.loads(sample_lines[0])
            if 'auth' in json_obj.get('service', '').lower() or any(kw in json_obj.get('message', '').lower() for kw in ['login', 'password', 'auth']):
                return AuthLogAnalyzer(file_path)
            else:
                return SystemLogAnalyzer(file_path)
        except json.JSONDecodeError:
            pass
    
    # 简单判断日志类型
    auth_keywords = ['sshd', 'login', 'password', 'authentication', 'session', 'user', 'account']
    auth_score = sum(1 for line in sample_lines if any(keyword in line.lower() for keyword in auth_keywords))
    
    if auth_score > 3:
        return AuthLogAnalyzer(file_path)
    else:
        return SystemLogAnalyzer(file_path)


def analyze_log_file(file_path):
    """
    模拟分析日志文件并返回结果
    """
    try:
        # 生成模拟的分析结果
        results = {
            'summary': {
                'total_lines': random.randint(1000, 5000),
                'start_time': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S'),
                'end_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'log_types': {
                    'INFO': random.randint(600, 3000),
                    'WARN': random.randint(100, 500),
                    'ERROR': random.randint(50, 200),
                    'DEBUG': random.randint(200, 1000)
                }
            },
            'anomalies': {
                'total_anomalies': random.randint(5, 20),
                'critical_anomalies': random.randint(1, 5),
                'warning_anomalies': random.randint(3, 15),
                'anomaly_types': [
                    {
                        'type': '异常登录尝试',
                        'count': random.randint(1, 10),
                        'severity': 'high'
                    },
                    {
                        'type': '系统资源使用异常',
                        'count': random.randint(1, 8),
                        'severity': 'medium'
                    },
                    {
                        'type': '服务响应超时',
                        'count': random.randint(1, 5),
                        'severity': 'low'
                    }
                ]
            },
            'trends': {
                'daily_events': generate_daily_data(),
                'error_distribution': {
                    'authentication': random.randint(10, 50),
                    'system': random.randint(20, 60),
                    'application': random.randint(15, 45),
                    'database': random.randint(5, 25)
                },
                'performance_metrics': {
                    'average_response_time': round(random.uniform(100, 500), 2),
                    'peak_response_time': round(random.uniform(500, 2000), 2),
                    'requests_per_minute': round(random.uniform(10, 100), 2)
                }
            }
        }
        
        return results
    except Exception as e:
        return {'error': str(e)}

def generate_daily_data():
    """生成每日数据统计"""
    daily_data = []
    base_date = datetime.now() - timedelta(days=7)
    
    for i in range(7):
        current_date = base_date + timedelta(days=i)
        daily_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'total_events': random.randint(1000, 5000),
            'error_events': random.randint(50, 200),
            'warning_events': random.randint(100, 500)
        })
    
    return daily_data 