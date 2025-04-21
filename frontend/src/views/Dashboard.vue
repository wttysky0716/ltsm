<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h1>态势感知仪表盘</h1>
      <div class="dashboard-controls">
        <span id="last-update-time">最后更新: --</span>
        <button id="refresh-button" class="refresh-btn">刷新数据</button>
            </div>
          </div>
    
    <div class="dashboard-grid">
      <div class="chart-container">
        <div id="alert-trend-chart" class="chart"></div>
            </div>
      <div class="chart-container">
        <div id="threat-gauge-chart" class="chart"></div>
            </div>
      <div class="chart-container">
        <div id="alert-types-chart" class="chart"></div>
          </div>
      <div class="chart-container">
        <div id="attack-map-chart" class="chart"></div>
            </div>
      <div class="chart-container">
        <div id="system-perf-chart" class="chart"></div>
            </div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts';
import DashboardUpdater from '../assets/js/dashboard.js';

export default {
  name: 'DashboardView',
  data() {
    return {
      dashboard: null
    }
  },
  mounted() {
    // 创建仪表盘实例并初始化
    this.dashboard = new DashboardUpdater(echarts);
    this.dashboard.initialize();
    
    // 添加手动刷新按钮事件
    document.getElementById('refresh-button').addEventListener('click', () => {
      this.dashboard.updateDashboard();
    });
  },
  beforeDestroy() {
    // 组件销毁前停止自动更新
    if (this.dashboard) {
      this.dashboard.stop();
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-gap: 20px;
}

.chart-container {
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.chart {
  height: 300px;
  width: 100%;
}

.refresh-btn {
  padding: 8px 16px;
  background: #409EFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style> 