<template>
  <app-layout>
    <div class="analysis-page">
      <div class="page-header">
        <div class="page-title">日志分析结果</div>
        <el-button type="primary" @click="goBack">返回文件列表</el-button>
      </div>
      
      <div v-if="loading" class="loading-container">
        <el-spinner type="primary"></el-spinner>
        <div>正在加载分析结果...</div>
      </div>
      
      <div v-else-if="errorMessage" class="error-container">
        <el-alert
          :title="errorMessage"
          type="error"
          show-icon>
        </el-alert>
      </div>
      
      <div v-else class="analysis-content">
        <h2>日志分析结果</h2>
        
        <!-- 文件信息 -->
        <el-card class="analysis-section">
          <div slot="header">
            <span>文件信息</span>
          </div>
          <div class="file-info">
            <p><strong>文件名：</strong>{{ file.original_filename }}</p>
            <p><strong>大小：</strong>{{ formatFileSize(file.file_size) }}</p>
            <p><strong>上传时间：</strong>{{ file.upload_time }}</p>
          </div>
        </el-card>
        
        <!-- 概要信息 -->
        <el-card class="analysis-section" v-if="results && results.summary">
          <div slot="header">
            <span>概要信息</span>
          </div>
          <div class="summary-info">
            <el-row :gutter="20">
              <el-col :span="6">
                <div class="stat-card">
                  <div class="stat-title">总行数</div>
                  <div class="stat-value">{{ results.summary.total_lines }}</div>
                </div>
              </el-col>
              <el-col :span="6" v-for="(value, type) in results.summary.log_types" :key="type">
                <div class="stat-card">
                  <div class="stat-title">{{ type }}</div>
                  <div class="stat-value">{{ value }}</div>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>
        
        <!-- 异常检测 -->
        <el-card class="analysis-section" v-if="results && results.anomalies">
          <div slot="header">
            <span>异常检测</span>
          </div>
          <div class="anomalies-info">
            <el-row :gutter="20">
              <el-col :span="8">
                <div class="stat-card danger">
                  <div class="stat-title">严重异常</div>
                  <div class="stat-value">{{ results.anomalies.critical_anomalies }}</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="stat-card warning">
                  <div class="stat-title">警告异常</div>
                  <div class="stat-value">{{ results.anomalies.warning_anomalies }}</div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="stat-card">
                  <div class="stat-title">总异常数</div>
                  <div class="stat-value">{{ results.anomalies.total_anomalies }}</div>
                </div>
              </el-col>
            </el-row>
            
            <div class="anomaly-types">
              <h4>异常类型分布</h4>
              <el-table :data="results.anomalies.anomaly_types" style="width: 100%">
                <el-table-column prop="type" label="类型"></el-table-column>
                <el-table-column prop="count" label="次数"></el-table-column>
                <el-table-column prop="severity" label="严重程度">
                  <template slot-scope="scope">
                    <el-tag :type="getSeverityType(scope.row.severity)">
                      {{ scope.row.severity }}
                    </el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </el-card>
        
        <!-- 趋势分析 -->
        <el-card class="analysis-section" v-if="results && results.trends">
          <div slot="header">
            <span>趋势分析</span>
          </div>
          <div class="trends-info">
            <div id="daily-events-chart" style="height: 400px"></div>
            
            <h4>错误分布</h4>
            <el-row :gutter="20">
              <el-col :span="6" v-for="(value, type) in results.trends.error_distribution" :key="type">
                <div class="stat-card">
                  <div class="stat-title">{{ type }}</div>
                  <div class="stat-value">{{ value }}</div>
                </div>
              </el-col>
            </el-row>
            
            <h4>性能指标</h4>
            <el-row :gutter="20">
              <el-col :span="8" v-for="(value, metric) in results.trends.performance_metrics" :key="metric">
                <div class="stat-card">
                  <div class="stat-title">{{ formatMetricName(metric) }}</div>
                  <div class="stat-value">{{ formatMetricValue(metric, value) }}</div>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </div>
    </div>
  </app-layout>
</template>

<script>
import AppLayout from '@/components/AppLayout.vue'
import * as echarts from 'echarts'

export default {
  name: 'Analysis',
  components: {
    AppLayout
  },
  data() {
    return {
      fileId: this.$route.params.id,
      file: null,
      results: null,
      loading: true,
      errorMessage: '',
      charts: {}
    }
  },
  created() {
    this.fetchFileData()
  },
  methods: {
    async fetchFileData() {
      this.loading = true
      
      try {
        // 获取文件信息
        const fileResponse = await this.$http.get(`/logs/${this.fileId}`)
        this.file = fileResponse
        
        // 获取分析结果
        try {
          const resultsResponse = await this.$http.get(`/analysis/results/${this.fileId}`)
          this.results = resultsResponse.results
          
          // 在下一个tick渲染图表
          this.$nextTick(() => {
            this.initCharts()
          })
        } catch (error) {
          console.error('Error fetching analysis results:', error)
          
          if (error.response && error.response.status === 404) {
            this.errorMessage = '还没有分析结果，请先分析该日志文件'
          } else {
            this.errorMessage = '获取分析结果失败'
          }
          
          this.results = null
        }
      } catch (error) {
        console.error('Error fetching file data:', error)
        this.file = null
        this.results = null
        this.errorMessage = '获取文件信息失败'
      } finally {
        this.loading = false
      }
    },
    
    initCharts() {
      if (!this.results || !this.results.trends || !this.results.trends.daily_events) {
        return
      }
      
      // 初始化每日事件图表
      const chartDom = document.getElementById('daily-events-chart')
      const myChart = echarts.init(chartDom)
      
      const dates = this.results.trends.daily_events.map(item => item.date)
      const totalEvents = this.results.trends.daily_events.map(item => item.total_events)
      const errorEvents = this.results.trends.daily_events.map(item => item.error_events)
      const warningEvents = this.results.trends.daily_events.map(item => item.warning_events)
      
      const option = {
        title: {
          text: '每日事件统计'
        },
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['总事件数', '错误事件', '警告事件']
        },
        xAxis: {
          type: 'category',
          data: dates
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '总事件数',
            type: 'line',
            data: totalEvents
          },
          {
            name: '错误事件',
            type: 'line',
            data: errorEvents
          },
          {
            name: '警告事件',
            type: 'line',
            data: warningEvents
          }
        ]
      }
      
      myChart.setOption(option)
      this.charts.dailyEvents = myChart
      
      // 监听窗口大小变化
      window.addEventListener('resize', () => {
        myChart.resize()
      })
    },
    
    formatFileSize(size) {
      const units = ['B', 'KB', 'MB', 'GB']
      let index = 0
      let fileSize = size
      
      while (fileSize >= 1024 && index < units.length - 1) {
        fileSize /= 1024
        index++
      }
      
      return `${fileSize.toFixed(2)} ${units[index]}`
    },
    
    getSeverityType(severity) {
      const types = {
        high: 'danger',
        medium: 'warning',
        low: 'info'
      }
      return types[severity] || 'info'
    },
    
    formatMetricName(metric) {
      const names = {
        average_response_time: '平均响应时间',
        peak_response_time: '峰值响应时间',
        requests_per_minute: '每分钟请求数'
      }
      return names[metric] || metric
    },
    
    formatMetricValue(metric, value) {
      if (metric.includes('response_time')) {
        return `${value} ms`
      }
      if (metric === 'requests_per_minute') {
        return `${value} req/min`
      }
      return value
    },
    
    goBack() {
      this.$router.push('/files')
    }
  },
  beforeDestroy() {
    // 清理图表实例
    Object.values(this.charts).forEach(chart => {
      chart.dispose()
    })
    
    // 移除事件监听
    window.removeEventListener('resize', () => {
      Object.values(this.charts).forEach(chart => {
        chart.resize()
      })
    })
  }
}
</script>

<style scoped>
.analysis-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.loading-container {
  text-align: center;
  padding: 40px;
}

.error-container {
  margin: 20px 0;
}

.analysis-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.analysis-section {
  margin-bottom: 20px;
}

.file-info {
  line-height: 1.8;
}

.summary-info,
.anomalies-info,
.trends-info {
  margin-top: 20px;
}

.stat-card {
  background: #f5f7fa;
  border-radius: 4px;
  padding: 15px;
  text-align: center;
  margin-bottom: 15px;
}

.stat-card.danger {
  background: #fef0f0;
}

.stat-card.warning {
  background: #fdf6ec;
}

.stat-title {
  color: #606266;
  font-size: 14px;
  margin-bottom: 10px;
}

.stat-value {
  color: #303133;
  font-size: 24px;
  font-weight: bold;
}

.anomaly-types {
  margin-top: 20px;
}

h4 {
  margin: 20px 0 15px;
  color: #303133;
}
</style> 