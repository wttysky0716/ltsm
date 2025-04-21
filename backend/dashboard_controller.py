import time
from datetime import datetime, timedelta
from data_generator import DataGenerator

class DashboardController:
    """仪表盘控制器，管理仪表盘数据的生成和更新"""
    
    def __init__(self, update_interval=10):
        """
        初始化仪表盘控制器
        参数:
            update_interval: 数据更新间隔(秒)
        """
        self.data_generator = DataGenerator()
        self.update_interval = update_interval
        self.last_update_time = 0
        self.dashboard_data = None
    
    def get_dashboard_data(self, force_update=False):
        """
        获取仪表盘数据，如果距离上次更新时间超过指定间隔，则更新数据
        参数:
            force_update: 是否强制更新数据
        返回:
            仪表盘数据
        """
        current_time = time.time()
        if force_update or self.dashboard_data is None or (current_time - self.last_update_time) >= self.update_interval:
            self.dashboard_data = self.data_generator.generate_complete_dashboard_data()
            self.last_update_time = current_time
        
        return self.dashboard_data
    
    def get_historical_data(self, days=7):
        """
        生成历史数据，用于趋势图表
        参数:
            days: 历史数据天数
        返回:
            历史数据列表
        """
        historical_data = []
        now = datetime.now()
        
        # 为每一天生成数据
        for i in range(days):
            # 使用不同的种子生成每一天的数据
            seed = int(time.time()) - (i * 86400)  # 每天的种子不同
            generator = DataGenerator(seed=seed)
            
            # 获取日期
            day = now - timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            
            # 生成当天的数据
            alerts = generator.generate_security_alerts()
            threat = generator.generate_threat_intelligence()
            
            historical_data.append({
                "date": day_str,
                "alert_count": alerts["total_alerts"],
                "threat_level": threat["threat_level"],
                "high_severity": alerts["severity_distribution"]["高危"]
            })
        
        # 按日期排序
        historical_data.sort(key=lambda x: x["date"])
        return historical_data 