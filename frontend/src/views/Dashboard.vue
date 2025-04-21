<template>
  <app-layout>
    <div class="dashboard-page">
      <div class="page-title">日志态势感知仪表盘</div>
      
      <el-row :gutter="20">
        <el-col :xs="24" :md="12" :lg="6">
          <div class="stat-card">
            <div class="stat-icon">
              <i class="el-icon-document"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ totalFiles }}</div>
              <div class="stat-label">总文件数</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :md="12" :lg="6">
          <div class="stat-card">
            <div class="stat-icon">
              <i class="el-icon-warning"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ totalAnomalies }}</div>
              <div class="stat-label">异常事件</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :md="12" :lg="6">
          <div class="stat-card">
            <div class="stat-icon">
              <i class="el-icon-success"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ loginSuccessRate }}%</div>
              <div class="stat-label">登录成功率</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :md="12" :lg="6">
          <div class="stat-card">
            <div class="stat-icon">
              <i class="el-icon-notebook-2"></i>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ totalEntries }}</div>
              <div class="stat-label">日志总条目</div>
            </div>
          </div>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" class="chart-row">
        <el-col :xs="24" :lg="12">
          <el-card class="chart-card">
            <div slot="header">
              <span>日志类型分布</span>
            </div>
            <div ref="logTypeChart" class="chart-container"></div>
          </el-card>
        </el-col>
        <el-col :xs="24" :lg="12">
          <el-card class="chart-card">
            <div slot="header">
              <span>告警趋势</span>
            </div>
            <div ref="alertTrendChart" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" class="chart-row">
        <el-col :span="24">
          <el-card class="chart-card">
            <div slot="header">
              <span>每日登录尝试分布</span>
            </div>
            <div ref="loginChart" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-row :gutter="20">
        <el-col :span="24">
          <el-card class="anomaly-card">
            <div slot="header">
              <span>最近异常</span>
            </div>
            <el-table :data="recentAnomalies" style="width: 100%">
              <el-table-column prop="timestamp" label="时间" width="180"></el-table-column>
              <el-table-column prop="type" label="类型" width="150">
                <template slot-scope="scope">
                  <el-tag :type="getAnomalyTagType(scope.row.severity)">{{ scope.row.type }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="description" label="描述"></el-table-column>
              <el-table-column prop="severity" label="严重程度" width="100">
                <template slot-scope="scope">
                  <el-tag :type="getAnomalyTagType(scope.row.severity)">{{ scope.row.severity }}</el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </app-layout>
</template>

<script>
import AppLayout from '@/components/AppLayout.vue'
import * as echarts from 'echarts'

export default {
  name: 'Dashboard',
  components: {
    AppLayout
  },
  data() {
    return {
      totalFiles: 0,
      totalAnomalies: 0,
      loginSuccessRate: 0,
      totalEntries: 0,
      recentAnomalies: [],
      charts: {}
    }
  },
  mounted() {
    this.fetchDashboardData()
    this.initCharts()
  },
  methods: {
    async fetchDashboardData() {
      // 这里是模拟数据，实际项目中应从API获取
      this.totalFiles = 12
      this.totalAnomalies = 32
      this.loginSuccessRate = 78.5
      this.totalEntries = 15782
      
      // 模拟最近异常数据
      this.recentAnomalies = [
        {
          timestamp: '2024-03-25 13:45:22',
          type: '用户登录失败',
          description: '用户admin在短时间内多次登录失败',
          severity: 'high'
        },
        {
          timestamp: '2024-03-25 12:30:15',
          type: 'IP异常访问',
          description: 'IP 192.168.1.45尝试多次访问受限资源',
          severity: 'medium'
        },
        {
          timestamp: '2024-03-25 10:12:08',
          type: '异常时间登录',
          description: '用户root在非工作时间尝试登录',
          severity: 'medium'
        },
        {
          timestamp: '2024-03-24 23:45:30',
          type: '高错误率',
          description: 'nginx服务器出现高比例的500错误',
          severity: 'high'
        },
        {
          timestamp: '2024-03-24 21:12:45',
          type: '异常行为模式',
          description: '检测到异常的文件访问模式',
          severity: 'low'
        }
      ]
    },
    
    initCharts() {
      this.$nextTick(() => {
        this.initLogTypeChart()
        this.initAlertTrendChart()
        this.initLoginChart()
      })
    },
    
    initLogTypeChart() {
      const chartDom = this.$refs.logTypeChart
      const chart = echarts.init(chartDom)
      
      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 10,
          data: ['认证日志', '系统日志', '应用日志', '安全日志', '其他']
        },
        series: [
          {
            name: '日志类型',
            type: 'pie',
            radius: ['50%', '70%'],
            avoidLabelOverlap: false,
            label: {
              show: false,
              position: 'center'
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '18',
                fontWeight: 'bold'
              }
            },
            labelLine: {
              show: false
            },
            data: [
              { value: 1048, name: '认证日志' },
              { value: 735, name: '系统日志' },
              { value: 580, name: '应用日志' },
              { value: 484, name: '安全日志' },
              { value: 300, name: '其他' }
            ]
          }
        ]
      }
      
      chart.setOption(option)
      this.charts.logType = chart
      
      window.addEventListener('resize', () => {
        chart.resize()
      })
    },
    
    initAlertTrendChart() {
      const chartDom = this.$refs.alertTrendChart
      const chart = echarts.init(chartDom)
      
      const option = {
        title: {
          text: '最近7天告警趋势'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          data: ['高危', '中危', '低危']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: ['3-19', '3-20', '3-21', '3-22', '3-23', '3-24', '3-25']
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '高危',
            type: 'bar',
            stack: 'total',
            emphasis: {
              focus: 'series'
            },
            data: [5, 3, 6, 8, 4, 9, 7],
            itemStyle: {
              color: '#F56C6C'
            }
          },
          {
            name: '中危',
            type: 'bar',
            stack: 'total',
            emphasis: {
              focus: 'series'
            },
            data: [12, 9, 15, 11, 13, 10, 14],
            itemStyle: {
              color: '#E6A23C'
            }
          },
          {
            name: '低危',
            type: 'bar',
            stack: 'total',
            emphasis: {
              focus: 'series'
            },
            data: [8, 10, 7, 9, 12, 8, 11],
            itemStyle: {
              color: '#909399'
            }
          }
        ]
      }
      
      chart.setOption(option)
      this.charts.alertTrend = chart
      
      window.addEventListener('resize', () => {
        chart.resize()
      })
    },
    
    initLoginChart() {
      const chartDom = this.$refs.loginChart
      const chart = echarts.init(chartDom)
      
      // 生成24小时的数据
      const hours = Array.from(Array(24).keys())
      const successData = [10, 5, 3, 2, 1, 0, 3, 15, 30, 25, 20, 18, 22, 25, 28, 30, 25, 20, 15, 12, 10, 8, 5, 3]
      const failureData = [2, 1, 1, 1, 0, 0, 1, 3, 5, 4, 3, 2, 3, 4, 5, 6, 4, 3, 2, 2, 2, 1, 1, 1]
      
      const option = {
        title: {
          text: '每小时登录尝试分布'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          data: ['成功', '失败']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: hours.map(h => `${h}:00`)
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '成功',
            type: 'line',
            smooth: true,
            data: successData,
            itemStyle: {
              color: '#67C23A'
            }
          },
          {
            name: '失败',
            type: 'line',
            smooth: true,
            data: failureData,
            itemStyle: {
              color: '#F56C6C'
            }
          }
        ]
      }
      
      chart.setOption(option)
      this.charts.login = chart
      
      window.addEventListener('resize', () => {
        chart.resize()
      })
    },
    
    getAnomalyTagType(severity) {
      const types = {
        'high': 'danger',
        'medium': 'warning',
        'low': 'info'
      }
      return types[severity] || 'info'
    }
  },
  beforeDestroy() {
    // 清理图表实例
    Object.values(this.charts).forEach(chart => {
      chart.dispose()
    })
  }
}
</script>

<style scoped>
.dashboard-page {
  max-width: 1200px;
  margin: 0 auto;
}

.stat-card {
  background-color: #fff;
  border-radius: 4px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
}

.stat-icon {
  font-size: 48px;
  color: #409EFF;
  margin-right: 20px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.chart-row {
  margin-bottom: 20px;
}

.chart-card {
  margin-bottom: 20px;
}

.chart-container {
  height: 300px;
}

.anomaly-card {
  margin-bottom: 20px;
}
</style> 