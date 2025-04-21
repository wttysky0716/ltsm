<template>
  <app-layout>
    <div class="file-list-page">
      <div class="page-header">
        <div class="page-title">日志文件列表</div>
        <el-button type="primary" @click="goToUpload">上传新文件</el-button>
      </div>
      
      <el-card class="file-list-card">
        <div slot="header">
          <div class="card-header">
            <span>您上传的所有日志文件</span>
            <el-input
              v-model="searchQuery"
              placeholder="搜索文件名"
              suffix-icon="el-icon-search"
              clearable
              style="width: 200px">
            </el-input>
          </div>
        </div>
        
        <el-table
          v-loading="loading"
          :data="filteredFiles"
          style="width: 100%"
          border
          stripe>
          <el-table-column
            type="index"
            width="50"
            align="center">
          </el-table-column>
          <el-table-column
            prop="original_filename"
            label="文件名"
            min-width="200">
          </el-table-column>
          <el-table-column
            prop="file_type"
            label="类型"
            width="100"
            align="center">
            <template slot-scope="scope">
              {{ scope.row.file_type || '未知' }}
            </template>
          </el-table-column>
          <el-table-column
            prop="file_size"
            label="大小"
            width="120"
            align="center">
            <template slot-scope="scope">
              {{ formatFileSize(scope.row.file_size) }}
            </template>
          </el-table-column>
          <el-table-column
            prop="upload_time"
            label="上传时间"
            width="180">
          </el-table-column>
          <el-table-column
            prop="status"
            label="状态"
            width="100"
            align="center">
            <template slot-scope="scope">
              <el-tag :type="getStatusType(scope.row.status)">
                {{ getStatusText(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            prop="processing_progress"
            label="进度"
            width="120"
            align="center">
            <template slot-scope="scope">
              <el-progress
                v-if="scope.row.status === 'processing'"
                :percentage="scope.row.processing_progress || 0"
                :stroke-width="14">
              </el-progress>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column
            label="操作"
            width="220"
            align="center">
            <template slot-scope="scope">
              <el-button
                size="mini"
                type="primary"
                :disabled="scope.row.status === 'processing'"
                @click="handleAnalyze(scope.row)">
                分析
              </el-button>
              <el-button
                size="mini"
                type="success"
                :disabled="scope.row.status !== 'completed'"
                @click="viewResults(scope.row)">
                查看结果
              </el-button>
              <el-button
                size="mini"
                type="danger"
                @click="handleDelete(scope.row)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="pagination-container">
          <el-pagination
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            :current-page="currentPage"
            :page-sizes="[10, 20, 50, 100]"
            :page-size="pageSize"
            layout="total, sizes, prev, pager, next, jumper"
            :total="total">
          </el-pagination>
        </div>
      </el-card>
    </div>
  </app-layout>
</template>

<script>
import AppLayout from '@/components/AppLayout.vue'
import { mapGetters } from 'vuex'

export default {
  name: 'FileList',
  components: {
    AppLayout
  },
  data() {
    return {
      searchQuery: '',
      currentPage: 1,
      pageSize: 10,
      total: 0,
      fileList: []
    }
  },
  computed: {
    ...mapGetters(['isLoading']),
    loading() {
      return this.isLoading
    },
    filteredFiles() {
      if (!this.searchQuery) {
        return this.fileList
      }
      
      const query = this.searchQuery.toLowerCase()
      return this.fileList.filter(file => 
        file.original_filename.toLowerCase().includes(query)
      )
    }
  },
  created() {
    this.fetchFiles()
  },
  methods: {
    async fetchFiles() {
      try {
        const response = await this.$http.get('/logs/list', {
          params: {
            page: this.currentPage,
            per_page: this.pageSize
          }
        })
        
        this.fileList = response.files
        this.total = response.total
      } catch (error) {
        console.error('Error fetching files:', error)
        this.$message.error('获取文件列表失败')
      }
    },
    
    formatFileSize(bytes) {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
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
    
    async handleAnalyze(file) {
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
          }
        } catch (error) {
          console.error('Error polling file status:', error)
        }
      }
      
      // 开始轮询
      setTimeout(pollStatus, 2000)
    },
    
    async handleDelete(file) {
      try {
        await this.$confirm(`确定要删除文件 "${file.original_filename}" 吗?`, '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        
        await this.$http.delete(`/logs/${file.id}`)
        this.$message.success('文件删除成功')
        
        // 刷新文件列表
        this.fetchFiles()
      } catch (error) {
        if (error === 'cancel') {
          // 用户取消删除
          return
        }
        
        console.error('Delete error:', error)
        let errorMsg = '删除文件失败'
        if (error.response && error.response.data) {
          errorMsg = error.response.data.message || errorMsg
        }
        this.$message.error(errorMsg)
      }
    },
    
    viewResults(file) {
      this.$router.push(`/analysis/${file.id}`)
    },
    
    goToUpload() {
      this.$router.push('/upload')
    },
    
    handleSizeChange(size) {
      this.pageSize = size
      this.fetchFiles()
    },
    
    handleCurrentChange(page) {
      this.currentPage = page
      this.fetchFiles()
    }
  }
}
</script>

<style scoped>
.file-list-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.file-list-card {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  text-align: right;
}
</style> 