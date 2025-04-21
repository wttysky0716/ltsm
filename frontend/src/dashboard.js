// 态势感知仪表盘前端脚本
class DashboardUpdater {
    constructor(updateInterval = 10000) {
        this.updateInterval = updateInterval; // 更新间隔，毫秒
        this.charts = {}; // 存储图表实例
        this.updateTimer = null;
    }

    // 初始化仪表盘
    initialize() {
        // 初始化所有图表
        this.initCharts();
        
        // 加载初始数据
        this.updateDashboard();
        
        // 设置定时更新
        this.updateTimer = setInterval(() => this.updateDashboard(), this.updateInterval);
        
        console.log("态势感知仪表盘初始化完成，数据将每" + (this.updateInterval/1000) + "秒更新一次");
    }
    
    // 初始化所有图表
    initCharts() {
        // 初始化告警趋势图
        this.charts.alertTrend = echarts.init(document.getElementById('alert-trend-chart'));
        
        // 初始化威胁级别仪表盘
        this.charts.threatGauge = echarts.init(document.getElementById('threat-gauge-chart'));
        
        // 初始化告警类型饼图
        this.charts.alertTypes = echarts.init(document.getElementById('alert-types-chart'));
        
        // 初始化攻击源地理分布图
        this.charts.attackMap = echarts.init(document.getElementById('attack-map-chart'));
        
        // 初始化系统性能监控图
        this.charts.systemPerformance = echarts.init(document.getElementById('system-perf-chart'));
    }
    
    // 更新仪表盘数据
    updateDashboard() {
        // 发起AJAX请求获取最新数据
        fetch('/api/dashboard-data')
            .then(response => response.json())
            .then(data => {
                // 更新各个图表
                this.updateAlertTrend(data.historical_data);
                this.updateThreatGauge(data.threat_intelligence.threat_level);
                this.updateAlertTypes(data.security_alerts.alert_types);
                this.updateAttackMap(data.threat_intelligence.attack_sources);
                this.updateSystemPerformance(data.system_performance);
                
                // 更新最后更新时间
                document.getElementById('last-update-time').textContent = 
                    '最后更新: ' + data.timestamp;
                
                console.log("仪表盘数据已更新");
            })
            .catch(error => {
                console.error("更新仪表盘数据失败:", error);
            });
    }
    
    // 以下是各个图表的更新方法
    updateAlertTrend(historicalData) {
        const option = {
            title: {
                text: '安全告警趋势'
            },
            tooltip: {
                trigger: 'axis'
            },
            legend: {
                data: ['总告警数', '高危告警']
            },
            xAxis: {
                type: 'category',
                data: historicalData.map(item => item.date)
            },
            yAxis: {
                type: 'value'
            },
            series: [
                {
                    name: '总告警数',
                    type: 'line',
                    data: historicalData.map(item => item.alert_count)
                },
                {
                    name: '高危告警',
                    type: 'line',
                    data: historicalData.map(item => item.high_severity)
                }
            ]
        };
        
        this.charts.alertTrend.setOption(option);
    }
    
    updateThreatGauge(threatLevel) {
        const option = {
            series: [{
                type: 'gauge',
                progress: {
                    show: true
                },
                detail: {
                    valueAnimation: true,
                    formatter: '{value}'
                },
                data: [{
                    value: threatLevel.toFixed(1),
                    name: '威胁指数'
                }],
                max: 100
            }]
        };
        
        this.charts.threatGauge.setOption(option);
    }
    
    updateAlertTypes(alertTypes) {
        const data = Object.entries(alertTypes).map(([name, value]) => ({
            name,
            value
        }));
        
        const option = {
            title: {
                text: '告警类型分布'
            },
            tooltip: {
                trigger: 'item',
                formatter: '{a} <br/>{b}: {c} ({d}%)'
            },
            series: [
                {
                    name: '告警类型',
                    type: 'pie',
                    radius: '70%',
                    data: data
                }
            ]
        };
        
        this.charts.alertTypes.setOption(option);
    }
    
    updateAttackMap(attackSources) {
        // 地图数据更新逻辑
        // 此处简化为柱状图
        const data = Object.entries(attackSources).map(([name, value]) => ({
            name,
            value
        }));
        
        const option = {
            title: {
                text: '攻击源分布'
            },
            tooltip: {},
            xAxis: {
                data: data.map(item => item.name)
            },
            yAxis: {},
            series: [{
                name: '攻击次数',
                type: 'bar',
                data: data.map(item => item.value)
            }]
        };
        
        this.charts.attackMap.setOption(option);
    }
    
    updateSystemPerformance(performance) {
        const option = {
            title: {
                text: '系统性能'
            },
            tooltip: {
                trigger: 'axis'
            },
            radar: {
                indicator: [
                    { name: 'CPU使用率', max: 100 },
                    { name: '内存使用率', max: 100 },
                    { name: '网络流量', max: 500 },
                    { name: '磁盘I/O', max: 100 }
                ]
            },
            series: [{
                type: 'radar',
                data: [
                    {
                        value: [
                            performance.cpu_usage,
                            performance.memory_usage,
                            performance.network_traffic/5, // 缩放到0-100范围
                            performance.disk_io
                        ],
                        name: '当前性能'
                    }
                ]
            }]
        };
        
        this.charts.systemPerformance.setOption(option);
    }
    
    // 停止自动更新
    stop() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
            console.log("仪表盘自动更新已停止");
        }
    }
}

// 页面加载完成后初始化仪表盘
document.addEventListener('DOMContentLoaded', () => {
    const dashboard = new DashboardUpdater();
    dashboard.initialize();
    
    // 添加手动刷新按钮事件
    document.getElementById('refresh-button').addEventListener('click', () => {
        dashboard.updateDashboard();
    });
}); 