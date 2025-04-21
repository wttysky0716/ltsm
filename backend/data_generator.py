import random
import numpy as np
import time
from datetime import datetime, timedelta

class DataGenerator:
    """数据生成器，用于生成具有随机性但符合业务规则的数据"""
    
    def __init__(self, seed=None):
        """
        初始化数据生成器
        参数:
            seed: 随机种子，如果为None则使用系统时间作为种子
        """
        # 如果没有指定种子，则使用当前时间作为种子
        if seed is None:
            seed = int(time.time())
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
        # 基础数据参数设置
        self.base_alert_count = 120  # 基础告警数量
        self.base_threat_level = 65  # 基础威胁等级
        self.weekly_pattern = [0.8, 1.0, 1.1, 1.2, 1.3, 0.9, 0.7]  # 周一到周日的流量模式
        
    def get_current_time_factor(self):
        """获取当前时间因子，根据时间模式生成合理的数据波动"""
        now = datetime.now()
        hour_factor = 0.5 + 0.5 * np.sin(np.pi * now.hour / 12)  # 时间因子，模拟一天内的波动
        weekday_factor = self.weekly_pattern[now.weekday()]  # 工作日模式
        return hour_factor * weekday_factor
    
    def generate_security_alerts(self):
        """生成安全告警数据"""
        time_factor = self.get_current_time_factor()
        # 基础值 + 随机波动 + 时间因子影响
        alert_count = int(self.base_alert_count * (0.8 + 0.4 * random.random()) * time_factor)
        
        # 告警类型分布
        alert_types = {
            "网络入侵": int(alert_count * (0.2 + 0.15 * random.random())),
            "恶意代码": int(alert_count * (0.15 + 0.1 * random.random())),
            "异常访问": int(alert_count * (0.3 + 0.2 * random.random())),
            "数据泄露": int(alert_count * (0.1 + 0.05 * random.random())),
            "其他": 0  # 将在下面计算以确保总和正确
        }
        # 确保总和等于alert_count
        alert_types["其他"] = alert_count - sum(alert_types.values())
        
        # 告警级别分布
        severity_distribution = {
            "高危": int(alert_count * (0.15 + 0.1 * random.random())),
            "中危": int(alert_count * (0.35 + 0.15 * random.random())),
            "低危": 0  # 将在下面计算以确保总和正确
        }
        severity_distribution["低危"] = alert_count - sum(severity_distribution.values())
        
        return {
            "total_alerts": alert_count,
            "alert_types": alert_types,
            "severity_distribution": severity_distribution
        }
    
    def generate_threat_intelligence(self):
        """生成威胁情报数据"""
        time_factor = self.get_current_time_factor()
        threat_level = self.base_threat_level * (0.9 + 0.2 * random.random()) * time_factor
        
        # 确保威胁等级在合理范围内
        threat_level = max(0, min(100, threat_level))
        
        # 生成攻击源IP地理分布
        attack_sources = {
            "北美": 25 + int(10 * random.random()),
            "欧洲": 20 + int(8 * random.random()),
            "亚洲": 35 + int(15 * random.random()),
            "其他": 0
        }
        attack_sources["其他"] = 100 - sum(attack_sources.values())
        
        return {
            "threat_level": threat_level,
            "attack_sources": attack_sources,
            "emerging_threats": self._generate_emerging_threats()
        }
    
    def _generate_emerging_threats(self):
        """生成新兴威胁数据"""
        threats = []
        threat_types = ["勒索软件", "钓鱼攻击", "DDoS", "供应链攻击", "零日漏洞"]
        threat_count = random.randint(2, 5)  # 随机生成2-5个新兴威胁
        
        for _ in range(threat_count):
            threat_type = random.choice(threat_types)
            severity = random.choices(["高", "中", "低"], weights=[0.3, 0.5, 0.2])[0]
            first_observed = datetime.now() - timedelta(days=random.randint(1, 30))
            
            threats.append({
                "type": threat_type,
                "severity": severity,
                "first_observed": first_observed.strftime("%Y-%m-%d"),
                "trend": random.choice(["上升", "稳定", "下降"])
            })
        
        return threats
    
    def generate_system_performance(self):
        """生成系统性能数据"""
        time_factor = self.get_current_time_factor()
        
        # CPU使用率
        cpu_usage = 35 + 25 * random.random() + 15 * time_factor
        cpu_usage = max(5, min(95, cpu_usage))  # 确保在合理范围内
        
        # 内存使用率
        memory_usage = 40 + 20 * random.random() + 10 * time_factor
        memory_usage = max(10, min(90, memory_usage))  # 确保在合理范围内
        
        # 网络流量 (Mbps)
        network_traffic = 180 + 120 * random.random() * time_factor
        
        # 磁盘I/O (MB/s)
        disk_io = 25 + 15 * random.random() * time_factor
        
        return {
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "network_traffic": network_traffic,
            "disk_io": disk_io
        }
    
    def generate_complete_dashboard_data(self):
        """生成完整的仪表盘数据"""
        # 使用当前时间更新种子，确保每次调用都有变化
        random.seed(int(time.time()))
        np.random.seed(int(time.time()))
        
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "security_alerts": self.generate_security_alerts(),
            "threat_intelligence": self.generate_threat_intelligence(),
            "system_performance": self.generate_system_performance(),
            "random_seed": int(time.time())  # 记录随机种子以便需要时可以重现
        } 