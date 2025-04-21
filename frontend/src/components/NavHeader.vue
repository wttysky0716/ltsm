<template>
  <el-header class="nav-header">
    <div class="logo">
      <router-link to="/">
        <span class="logo-text">日志态势感知系统</span>
      </router-link>
    </div>
    <div class="nav-menu">
      <el-menu
        :default-active="activeRoute"
        mode="horizontal"
        :router="true"
        background-color="#304156"
        text-color="#fff"
        active-text-color="#409EFF">
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/upload">上传日志</el-menu-item>
        <el-menu-item index="/files">日志列表</el-menu-item>
        <el-menu-item index="/dashboard">态势感知</el-menu-item>
      </el-menu>
    </div>
    <div class="user-info">
      <el-dropdown trigger="click" @command="handleCommand">
        <span class="el-dropdown-link">
          <span class="username">{{ username }}</span>
          <i class="el-icon-arrow-down el-icon--right"></i>
        </span>
        <el-dropdown-menu slot="dropdown">
          <el-dropdown-item command="profile">个人资料</el-dropdown-item>
          <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
        </el-dropdown-menu>
      </el-dropdown>
    </div>
  </el-header>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'NavHeader',
  computed: {
    ...mapGetters(['currentUser']),
    username() {
      return this.currentUser ? this.currentUser.username : '用户'
    },
    activeRoute() {
      return this.$route.path
    }
  },
  methods: {
    handleCommand(command) {
      if (command === 'logout') {
        this.logout()
      } else if (command === 'profile') {
        this.$router.push('/profile')
      }
    },
    logout() {
      this.$store.dispatch('logout')
      this.$router.push('/login')
      this.$message.success('已退出登录')
    }
  }
}
</script>

<style scoped>
.nav-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  background-color: #304156;
  color: #fff;
  padding: 0 20px;
}

.logo {
  height: 100%;
  display: flex;
  align-items: center;
}

.logo a {
  text-decoration: none;
  color: #fff;
}

.logo-text {
  font-size: 20px;
  font-weight: bold;
}

.nav-menu {
  flex: 1;
  margin: 0 20px;
}

.nav-menu .el-menu {
  border-bottom: none;
}

.user-info {
  display: flex;
  align-items: center;
}

.el-dropdown-link {
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.username {
  margin-right: 5px;
}
</style> 