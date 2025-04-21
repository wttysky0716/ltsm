<template>
  <app-layout>
    <div class="register-container">
      <div class="register-card">
        <div class="register-header">
          <h2 class="title">日志态势感知系统</h2>
          <p class="subtitle">创建新账户</p>
        </div>
        
        <el-form
          ref="registerForm"
          :model="registerForm"
          :rules="registerRules"
          class="register-form"
          label-position="top"
          @submit.native.prevent="handleRegister">
          
          <el-form-item label="用户名" prop="username">
            <el-input 
              v-model="registerForm.username"
              prefix-icon="el-icon-user"
              placeholder="请输入用户名"
              clearable>
            </el-input>
          </el-form-item>
          
          <el-form-item label="邮箱" prop="email">
            <el-input 
              v-model="registerForm.email"
              prefix-icon="el-icon-message"
              placeholder="请输入邮箱"
              clearable>
            </el-input>
          </el-form-item>
          
          <el-form-item label="密码" prop="password">
            <el-input 
              v-model="registerForm.password"
              prefix-icon="el-icon-lock"
              placeholder="请输入密码"
              show-password
              clearable>
            </el-input>
          </el-form-item>
          
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input 
              v-model="registerForm.confirmPassword"
              prefix-icon="el-icon-lock"
              placeholder="请再次输入密码"
              show-password
              clearable>
            </el-input>
          </el-form-item>
          
          <el-form-item>
            <el-button 
              :loading="loading"
              type="primary"
              class="register-button"
              @click="handleRegister">
              注册
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="register-footer">
          <p>已有账户？ <router-link to="/login">立即登录</router-link></p>
        </div>
      </div>
    </div>
  </app-layout>
</template>

<script>
import AppLayout from '@/components/AppLayout.vue'
import { mapGetters } from 'vuex'

export default {
  name: 'Register',
  components: {
    AppLayout
  },
  data() {
    // 确认密码的验证规则
    const validateConfirmPassword = (rule, value, callback) => {
      if (value !== this.registerForm.password) {
        callback(new Error('两次输入密码不一致!'))
      } else {
        callback()
      }
    }
    
    return {
      registerForm: {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      },
      registerRules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        email: [
          { required: true, message: '请输入邮箱地址', trigger: 'blur' },
          { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, max: 30, message: '长度在 6 到 30 个字符', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请再次输入密码', trigger: 'blur' },
          { validator: validateConfirmPassword, trigger: 'blur' }
        ]
      }
    }
  },
  computed: {
    ...mapGetters(['isLoading']),
    loading() {
      return this.isLoading
    }
  },
  methods: {
    handleRegister() {
      this.$refs.registerForm.validate(async valid => {
        if (valid) {
          try {
            // 使用解构赋值并实际使用confirmPassword变量
            const { username, email, password, confirmPassword } = this.registerForm;
            
            // 确认两次密码输入一致
            if (password !== confirmPassword) {
              this.$message.error('两次输入密码不一致');
              return;
            }
            
            // 实际注册只需要传递username, email, password
            const userData = { username, email, password };
            
            await this.$store.dispatch('register', userData)
            this.$message.success('注册成功')
            this.$router.push('/')
          } catch (error) {
            let errorMsg = '注册失败'
            if (error.response && error.response.data) {
              errorMsg = error.response.data.message || errorMsg
            }
            this.$message.error(errorMsg)
          }
        } else {
          console.log('表单验证失败')
          return false
        }
      })
    }
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}

.register-card {
  width: 400px;
  padding: 30px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.register-header .title {
  margin: 0;
  font-size: 24px;
  color: #303133;
  margin-bottom: 10px;
}

.register-header .subtitle {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.register-form {
  margin-bottom: 20px;
}

.register-button {
  width: 100%;
}

.register-footer {
  text-align: center;
  font-size: 14px;
  color: #606266;
}

.register-footer a {
  color: #409EFF;
  text-decoration: none;
}
</style> 