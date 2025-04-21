<template>
  <app-layout>
    <div class="home-page">
      <el-row :gutter="20">
        <el-col :xs="24" :md="8">
          <div class="feature-card">
            <div class="feature-icon">
              <i class="el-icon-upload"></i>
            </div>
            <h3 class="feature-title">上传日志</h3>
            <p class="feature-desc">支持各种离线日志文件的上传，包括系统日志、认证日志等。</p>
            <el-button type="primary" @click="goToUpload">开始上传</el-button>
          </div>
        </el-col>
        <el-col :xs="24" :md="8">
          <div class="feature-card">
            <div class="feature-icon">
              <i class="el-icon-data-analysis"></i>
            </div>
            <h3 class="feature-title">日志分析</h3>
            <p class="feature-desc">智能分析日志内容，提取重要信息，检测异常行为和潜在威胁。</p>
            <el-button type="primary" @click="goToFiles">查看分析</el-button>
          </div>
        </el-col>
        <el-col :xs="24" :md="8">
          <div class="feature-card">
            <div class="feature-icon">
              <i class="el-icon-monitor"></i>
            </div>
            <h3 class="feature-title">态势感知</h3>
            <p class="feature-desc">基于日志分析结果，展示系统安全态势，预测潜在风险和趋势。</p>
            <el-button type="primary" @click="goToDashboard">查看态势</el-button>
          </div>
        </el-col>
      </el-row>
      
      <el-divider content-position="center">最近上传的文件</el-divider>
      
      <el-table
        v-if="recentFiles.length > 0"
        :data="recentFiles"
        stripe
        style="width: 100%">
        <el-table-column
          prop="original_filename"
          label="文件名">
        </el-table-column>
        <el-table-column
          prop="upload_time"
          label="上传时间"
          width="180">
        </el-table-column>
        <el-table-column
          prop="status"
          label="状态"
          width="120">
          <template slot-scope="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          label="操作"
          width="180">
          <template slot-scope="scope">
            <el-button
              size="mini"
              type="primary"
              @click="viewFile(scope.row)"
              :disabled="scope.row.status !== 'completed'">
              查看分析
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div v-else class="no-data">
        <i class="el-icon-document"></i>
        <p>暂无上传文件</p>
        <el-button type="primary" @click="goToUpload">立即上传</el-button>
      </div>
    </div>
  </app-layout>
</template>

<script>
import AppLayout from '@/components/AppLayout.vue'

export default {
  name: 'Home',
  components: {
    AppLayout
  },
  data() {
    return {
      recentFiles: []
    }
  },
  created() {
    this.fetchRecentFiles()
  },
  methods: {
    async fetchRecentFiles() {
      try {
        const response = await this.$store.dispatch('fetchLogFiles')
        this.recentFiles = response.files.slice(0, 5) // 只显示最近5个文件
      } catch (error) {
        console.error('Error fetching files:', error)
      }
    },
    getStatusType(status) {
      const statusMap = {
        'pending': 'info',
        'processing': 'warning',
        'completed': 'success',
        'failed': 'danger'
      }
      return statusMap[status] || 'info'
    },
    getStatusText(status) {
      const statusMap = {
        'pending': '等待处理',
        'processing': '处理中',
        'completed': '已完成',
        'failed': '处理失败'
      }
      return statusMap[status] || status
    },
    viewFile(file) {
      this.$router.push(`/analysis/${file.id}`)
    },
    goToUpload() {
      this.$router.push('/upload')
    },
    goToFiles() {
      this.$router.push('/files')
    },
    goToDashboard() {
      this.$router.push('/dashboard')
    }
  }
}
</script>

<style scoped>
.home-page {
  max-width: 1200px;
  margin: 0 auto;
}

.feature-card {
  height: 100%;
  padding: 30px;
  text-align: center;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  transition: all 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  font-size: 48px;
  color: #409EFF;
  margin-bottom: 20px;
}

.feature-title {
  font-size: 20px;
  color: #303133;
  margin: 0 0 15px 0;
}

.feature-desc {
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
  margin-bottom: 20px;
  height: 60px;
}

.el-divider {
  margin: 30px 0;
}

.no-data {
  padding: 50px 0;
  text-align: center;
  color: #909399;
}

.no-data i {
  font-size: 48px;
  margin-bottom: 20px;
}

.no-data p {
  margin-bottom: 20px;
}
</style> 