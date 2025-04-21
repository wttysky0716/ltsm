<template>
  <div class="upload-progress">
    <div class="progress-info">
      <span class="file-name">{{ file.original_filename }}</span>
      <span class="progress-percent">{{ progressText }}</span>
    </div>
    <el-progress 
      :percentage="progressValue" 
      :status="progressStatus"
      :stroke-width="12"
      :color="progressColor">
    </el-progress>
    <div class="file-meta">
      <span class="file-size">大小: {{ formatFileSize(file.file_size) }}</span>
      <span class="file-status">状态: {{ statusText }}</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UploadProgress',
  props: {
    file: {
      type: Object,
      required: true
    }
  },
  computed: {
    progressValue() {
      return this.file.processing_progress || 0
    },
    progressText() {
      return `${this.progressValue.toFixed(1)}%`
    },
    progressStatus() {
      if (this.file.status === 'completed') {
        return 'success'
      } else if (this.file.status === 'failed') {
        return 'exception'
      }
      return ''
    },
    progressColor() {
      if (this.file.status === 'pending') {
        return '#909399'
      } else if (this.file.status === 'processing') {
        return '#409EFF'
      } else if (this.file.status === 'completed') {
        return '#67C23A'
      } else if (this.file.status === 'failed') {
        return '#F56C6C'
      }
      return ''
    },
    statusText() {
      const statusMap = {
        'pending': '等待处理',
        'processing': '处理中',
        'completed': '已完成',
        'failed': '处理失败'
      }
      return statusMap[this.file.status] || this.file.status
    }
  },
  methods: {
    formatFileSize(bytes) {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }
  }
}
</script>

<style scoped>
.upload-progress {
  margin-bottom: 15px;
  padding: 15px;
  border-radius: 4px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.file-name {
  font-weight: 500;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 70%;
}

.progress-percent {
  color: #606266;
  font-weight: 500;
}

.file-meta {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 13px;
  color: #909399;
}
</style> 