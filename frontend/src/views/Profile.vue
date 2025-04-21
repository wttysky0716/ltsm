<template>
  <app-layout>
    <div class="profile-page">
      <div class="page-title">个人资料</div>
      
      <el-row :gutter="20">
        <el-col :md="8" :xs="24">
          <el-card class="user-card">
            <div class="user-avatar">
              <i class="el-icon-user-solid"></i>
            </div>
            <h3 class="user-name">{{ user.username }}</h3>
            <p class="user-email">{{ user.email }}</p>
            <p class="user-joined">注册时间: {{ formatDate(user.created_at) }}</p>
          </el-card>
          
          <el-card class="stats-card">
            <div slot="header">
              <span>使用统计</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">已上传文件</span>
              <span class="stat-value">{{ fileStats.totalFiles }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">已分析文件</span>
              <span class="stat-value">{{ fileStats.analyzedFiles }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">待处理文件</span>
              <span class="stat-value">{{ fileStats.pendingFiles }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">已检测异常</span>
              <span class="stat-value">{{ fileStats.totalAnomalies }}</span>
            </div>
          </el-card>
        </el-col>
        
        <el-col :md="16" :xs="24">
          <el-card class="form-card">
            <div slot="header">
              <span>修改个人资料</span>
            </div>
            <el-form 
              ref="profileForm" 
              :model="profileForm" 
              :rules="rules" 
              label-width="120px">
              <el-form-item label="用户名" prop="username">
                <el-input v-model="profileForm.username"></el-input>
              </el-form-item>
              <el-form-item label="邮箱" prop="email">
                <el-input v-model="profileForm.email"></el-input>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="updateProfile">保存修改</el-button>
              </el-form-item>
            </el-form>
          </el-card>
          
          <el-card class="form-card">
            <div slot="header">
              <span>修改密码</span>
            </div>
            <el-form 
              ref="passwordForm" 
              :model="passwordForm" 
              :rules="passwordRules" 
              label-width="120px">
              <el-form-item label="当前密码" prop="currentPassword">
                <el-input type="password" v-model="passwordForm.currentPassword" show-password></el-input>
              </el-form-item>
              <el-form-item label="新密码" prop="newPassword">
                <el-input type="password" v-model="passwordForm.newPassword" show-password></el-input>
              </el-form-item>
              <el-form-item label="确认新密码" prop="confirmPassword">
                <el-input type="password" v-model="passwordForm.confirmPassword" show-password></el-input>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="updatePassword">修改密码</el-button>
              </el-form-item>
            </el-form>
          </el-card>
          
          <el-card class="recent-activity-card">
            <div slot="header">
              <span>最近活动</span>
            </div>
            <el-timeline>
              <el-timeline-item
                v-for="(activity, index) in recentActivities"
                :key="index"
                :timestamp="activity.time"
                :color="activity.color">
                {{ activity.content }}
              </el-timeline-item>
            </el-timeline>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </app-layout>
</template>

<script>
import AppLayout from '@/components/AppLayout.vue'
import { mapGetters } from 'vuex'

export default {
  name: 'Profile',
  components: {
    AppLayout
  },
  data() {
    // 密码验证规则
    const validatePass = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请输入密码'))
      } else {
        if (this.passwordForm.confirmPassword !== '') {
          this.$refs.passwordForm.validateField('confirmPassword')
        }
        callback()
      }
    }
    const validatePass2 = (rule, value, callback) => {
      if (value === '') {
        callback(new Error('请再次输入密码'))
      } else if (value !== this.passwordForm.newPassword) {
        callback(new Error('两次输入密码不一致!'))
      } else {
        callback()
      }
    }
    
    return {
      profileForm: {
        username: '',
        email: ''
      },
      passwordForm: {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      },
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        email: [
          { required: true, message: '请输入邮箱地址', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
        ]
      },
      passwordRules: {
        currentPassword: [
          { required: true, message: '请输入当前密码', trigger: 'blur' }
        ],
        newPassword: [
          { required: true, message: '请输入新密码', trigger: 'blur' },
          { validator: validatePass, trigger: 'blur' },
          { min: 6, message: '密码长度不能小于6个字符', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请再次输入新密码', trigger: 'blur' },
          { validator: validatePass2, trigger: 'blur' }
        ]
      },
      fileStats: {
        totalFiles: 0,
        analyzedFiles: 0,
        pendingFiles: 0,
        totalAnomalies: 0
      },
      recentActivities: [
        { content: '上传了日志文件 server.log', time: '2024-03-25 13:25', color: '#409EFF' },
        { content: '分析了日志文件 auth.log', time: '2024-03-24 16:43', color: '#67C23A' },
        { content: '检测到7个异常', time: '2024-03-24 16:45', color: '#E6A23C' },
        { content: '上传了日志文件 access.log', time: '2024-03-23 10:15', color: '#409EFF' },
        { content: '修改了个人资料', time: '2024-03-22 09:30', color: '#909399' }
      ]
    }
  },
  computed: {
    ...mapGetters(['currentUser']),
    user() {
      return this.currentUser || {}
    }
  },
  created() {
    this.loadUserData()
    this.fetchUserStats()
  },
  methods: {
    loadUserData() {
      if (this.user) {
        this.profileForm.username = this.user.username
        this.profileForm.email = this.user.email
      }
    },
    
    async fetchUserStats() {
      // 这里是模拟数据，实际项目中应从API获取
      this.fileStats = {
        totalFiles: 8,
        analyzedFiles: 5,
        pendingFiles: 3,
        totalAnomalies: 12
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString()
    },
    
    async updateProfile() {
      this.$refs.profileForm.validate(async valid => {
        if (valid) {
          try {
            // 这里应该有实际的API调用来更新用户资料
            // await this.$http.put('/api/user/profile', this.profileForm)
            
            this.$message.success('个人资料更新成功')
          } catch (error) {
            console.error('Update profile error:', error)
            this.$message.error('更新个人资料失败')
          }
        } else {
          return false
        }
      })
    },
    
    async updatePassword() {
      this.$refs.passwordForm.validate(async valid => {
        if (valid) {
          try {
            // 这里应该有实际的API调用来更新密码
            // await this.$http.put('/api/user/password', this.passwordForm)
            
            this.$message.success('密码修改成功')
            this.passwordForm.currentPassword = ''
            this.passwordForm.newPassword = ''
            this.passwordForm.confirmPassword = ''
          } catch (error) {
            console.error('Update password error:', error)
            this.$message.error('密码修改失败')
          }
        } else {
          return false
        }
      })
    }
  }
}
</script>

<style scoped>
.profile-page {
  max-width: 1200px;
  margin: 0 auto;
}

.user-card {
  text-align: center;
  padding: 30px 20px;
  margin-bottom: 20px;
}

.user-avatar {
  font-size: 80px;
  color: #409EFF;
  margin-bottom: 20px;
}

.user-name {
  font-size: 22px;
  font-weight: 500;
  margin: 0;
  color: #303133;
}

.user-email {
  font-size: 14px;
  color: #606266;
  margin: 10px 0;
}

.user-joined {
  font-size: 12px;
  color: #909399;
}

.stats-card {
  margin-bottom: 20px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #EBEEF5;
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  color: #606266;
}

.stat-value {
  font-weight: 500;
  color: #303133;
}

.form-card {
  margin-bottom: 20px;
}

.recent-activity-card {
  margin-bottom: 20px;
}
</style> 