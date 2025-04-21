<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h2 class="title">日志态势感知系统</h2>
        <p class="subtitle">登录您的账户</p>
      </div>
      
      <el-form
        ref="loginForm"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        label-position="top"
        @submit.native.prevent="handleLogin">
        
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model="loginForm.username"
            prefix-icon="el-icon-user"
            placeholder="请输入用户名"
            clearable>
          </el-input>
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="loginForm.password"
            prefix-icon="el-icon-lock"
            placeholder="请输入密码"
            show-password
            clearable>
          </el-input>
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="rememberMe">记住我</el-checkbox>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            :loading="loading"
            type="primary"
            class="login-button"
            @click="handleLogin">
            登录
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-footer">
        <p>还没有账户？ <router-link to="/register">立即注册</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'Login',
  data() {
    return {
      loginForm: {
        username: '',
        password: ''
      },
      loginRules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, max: 30, message: '长度在 6 到 30 个字符', trigger: 'blur' }
        ]
      },
      rememberMe: false,
      redirect: undefined
    }
  },
  computed: {
    ...mapGetters(['isLoading']),
    loading() {
      return this.isLoading
    }
  },
  watch: {
    $route: {
      handler(route) {
        this.redirect = route.query && route.query.redirect
      },
      immediate: true
    }
  },
  methods: {
    handleLogin() {
      this.$refs.loginForm.validate(async valid => {
        if (valid) {
          try {
            console.log('开始登录请求，用户名:', this.loginForm.username);
            
            // 清除任何之前的登录状态
            this.$store.dispatch('logout');
            
            // 尝试登录
            const response = await this.$store.dispatch('login', this.loginForm)
            console.log('登录响应:', response);
            
            // 验证登录状态
            if (!this.$store.state.authenticated || !this.$store.state.token) {
              throw new Error('登录后状态无效');
            }
            
            this.$message.success('登录成功')
            
            // 延迟后跳转，确保状态已更新
            setTimeout(() => {
              // 重定向到之前尝试访问的页面或首页
              const path = this.redirect || '/';
              console.log('重定向到:', path);
              this.$router.push({ path });
            }, 300);
            
          } catch (error) {
            console.error('登录处理错误:', error);
            
            let errorMsg = '登录失败';
            if (error.response && error.response.data) {
              console.error('服务器错误响应:', error.response.data);
              errorMsg = error.response.data.message || errorMsg;
            } else if (error.message) {
              errorMsg = error.message;
            }
            
            this.$message.error(errorMsg);
          }
        } else {
          console.log('表单验证失败');
          return false;
        }
      });
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}

.login-card {
  width: 400px;
  padding: 30px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header .title {
  margin: 0;
  font-size: 24px;
  color: #303133;
  margin-bottom: 10px;
}

.login-header .subtitle {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.login-form {
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
}

.login-footer {
  text-align: center;
  font-size: 14px;
  color: #606266;
}

.login-footer a {
  color: #409EFF;
  text-decoration: none;
}
</style> 