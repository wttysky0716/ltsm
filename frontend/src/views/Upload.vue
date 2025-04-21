<template>
  <app-layout>
    <div class="upload-page">
      <div class="page-title">上传日志文件</div>
      
      <el-card class="upload-card">
        <div class="upload-area" @click="triggerUpload">
          <i class="el-icon-upload upload-icon"></i>
          <div class="upload-text">点击或拖拽文件到此区域上传</div>
          <div class="upload-tip">支持 .log, .txt, .csv, .json 等格式文件</div>
          <input 
            ref="fileInput"
            type="file"
            class="file-input"
            @change="handleFileChange"
            accept=".log,.txt,.csv,.json"
            style="display: none">
        </div>
        
        <div v-if="fileList.length > 0" class="upload-list">
          <h3>已上传文件</h3>
          <div v-for="(file, index) in fileList" :key="index" class="upload-item">
            <upload-progress :file="file" />
            <div class="upload-actions">
              <el-button 
                type="primary" 
                size="small" 
                :disabled="file.status === 'processing'"
                @click="handleAnalyze(file)">
                分析
              </el-button>
              <el-button 
                type="success" 
                size="small" 
                :disabled="file.status !== 'completed'"
                @click="viewResults(file)">
                查看结果
              </el-button>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </app-layout>
</template>

<script>
import AppLayout from '@/components/AppLayout.vue'
import UploadProgress from '@/components/UploadProgress.vue'

export default {
  name: 'Upload',
  components: {
    AppLayout,
    UploadProgress
  },
  data() {
    return {
      fileList: [],
      uploadProgress: 0,
      uploading: false
    }
  },
  created() {
    this.fetchRecentFiles()
  },
  methods: {
    async fetchRecentFiles() {
      try {
        const response = await this.$store.dispatch('fetchLogFiles')
        this.fileList = response.files.slice(0, 5) // 只显示最近5个文件
      } catch (error) {
        console.error('Error fetching files:', error)
        this.$message.error('获取文件列表失败')
      }
    },
    
    triggerUpload() {
      if (this.uploading) {
        this.$message.warning('正在上传文件，请稍候...')
        return
      }
      this.$refs.fileInput.click()
    },
    
    async handleFileChange(event) {
      try {
        const file = event.target.files[0]
        if (!file) {
          console.warn('No file selected');
          return;
        }
        
        console.log('Selected file:', file.name, file.type, file.size);
        
        // 检查文件大小
        const maxSize = 500 * 1024 * 1024 // 500MB
        if (file.size > maxSize) {
          this.$message.error(`文件大小不能超过500MB，当前文件大小：${(file.size / (1024 * 1024)).toFixed(2)}MB`)
          event.target.value = ''
          return
        }
        
        // 检查文件扩展名
        const extension = file.name.split('.').pop().toLowerCase()
        const allowedExtensions = ['log', 'txt', 'csv', 'json']
        if (!allowedExtensions.includes(extension)) {
          this.$message.error(`不支持的文件类型：${extension}，支持的类型：${allowedExtensions.join(', ')}`)
          event.target.value = ''
          return
        }
        
        // 创建表单数据
        const formData = new FormData()
        formData.append('file', file)
        
        this.uploading = true
        const loadingInstance = this.$loading({
          lock: true,
          text: `正在上传文件：${file.name}...`,
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)'
        })
        
        try {
          console.log('开始上传文件:', file.name)
          
          // 检查token是否存在
          const token = this.$store.state.token
          console.log('Token exists:', !!token);
          
          const response = await this.$store.dispatch('uploadLogFile', formData)
          console.log('上传响应:', response)
          
          this.$message.success(`文件 ${file.name} 上传成功`)
          
          // 将新上传的文件添加到列表
          this.fileList.unshift(response.file)
          
        } catch (error) {
          console.error('Upload component error:', error)
          
          // 详细记录错误
          if (error.response) {
            console.error('Status:', error.response.status);
            console.error('Headers:', error.response.headers);
            console.error('Data:', error.response.data);
          } else if (error.request) {
            console.error('Request made but no response:', error.request);
          } else {
            console.error('Error message:', error.message);
          }
          
          let errorMsg = '文件上传失败'
          if (error.response && error.response.data) {
            const detail = error.response.data.detail || ''
            errorMsg = `${error.response.data.message || errorMsg}${detail ? ': ' + detail : ''}`
          }
          this.$message.error(errorMsg)
        } finally {
          // 重置文件输入框
          event.target.value = ''
          this.uploading = false
          loadingInstance.close()
        }
      } catch (globalError) {
        console.error('全局错误:', globalError);
        this.$message.error('上传过程中发生错误，请查看控制台');
        event.target.value = '';
        this.uploading = false;
      }
    },
    
    async handleAnalyze(file) {
      if (file.status === 'processing') {
        this.$message.warning('文件正在处理中，请稍候...')
        return
      }
      
      try {
        await this.$store.dispatch('analyzeLogFile', file.id)
        this.$message.success('开始分析日志文件')
        
        // 更新文件状态
        const index = this.fileList.findIndex(f => f.id === file.id)
        if (index !== -1) {
          this.$set(this.fileList[index], 'status', 'processing')
          this.$set(this.fileList[index], 'processing_progress', 0)
        }
        
        // 轮询文件处理状态
        this.pollFileStatus(file.id)
      } catch (error) {
        console.error('Analysis error:', error)
        let errorMsg = '开始分析失败'
        if (error.response && error.response.data) {
          errorMsg = error.response.data.message || errorMsg
        }
        this.$message.error(errorMsg)
      }
    },
    
    async pollFileStatus(fileId) {
      // 创建轮询函数
      const pollStatus = async () => {
        try {
          const response = await this.$http.get(`/logs/${fileId}`)
          const file = response
          
          // 更新文件状态
          const index = this.fileList.findIndex(f => f.id === fileId)
          if (index !== -1) {
            this.$set(this.fileList, index, file)
          }
          
          // 如果还在处理中，继续轮询
          if (file.status === 'processing') {
            setTimeout(pollStatus, 2000) // 每2秒轮询一次
          } else if (file.status === 'completed') {
            this.$message.success('文件分析完成')
          } else if (file.status === 'failed') {
            this.$message.error('文件分析失败')
          }
        } catch (error) {
          console.error('Error polling file status:', error)
          this.$message.error('获取文件状态失败')
        }
      }
      
      // 开始轮询
      setTimeout(pollStatus, 2000)
    },
    
    viewResults(file) {
      if (file.status !== 'completed') {
        this.$message.warning('请等待文件分析完成后查看结果')
        return
      }
      this.$router.push(`/analysis/${file.id}`)
    }
  }
}
</script>

<style scoped>
.upload-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.page-title {
  font-size: 24px;
  color: #303133;
  margin-bottom: 20px;
}

.upload-card {
  margin-bottom: 20px;
}

.upload-area {
  border: 2px dashed #dcdfe6;
  border-radius: 6px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.upload-area:hover {
  border-color: #409eff;
}

.upload-icon {
  font-size: 48px;
  color: #909399;
  margin-bottom: 20px;
}

.upload-text {
  font-size: 16px;
  color: #606266;
  margin-bottom: 10px;
}

.upload-tip {
  font-size: 14px;
  color: #909399;
}

.file-input {
  display: none;
}

.upload-list {
  margin-top: 20px;
}

.upload-list h3 {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 15px;
  color: #303133;
}

.upload-item {
  margin-bottom: 15px;
}

.upload-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: -10px;
}
</style> 