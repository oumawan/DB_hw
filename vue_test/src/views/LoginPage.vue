<template>
  <div class="login-container">
    <h2>登录</h2>
    <input type="email" v-model="email" placeholder="邮箱">
    <input type="password" v-model="password" placeholder="密码">
    <button @click="login" :disabled="loading">{{ loading ? '登录中...' : '登录' }}</button>
    
  </div>
</template>

<script>
import {apiService} from '../api/api.js'
import service from '../plugins/messageService'
import { saveUserToLocal } from '@/plugins/storage.js';

export default {
  name: 'LoginPage',
  data() {
    return {
      email: '',
      password: '',
      loading: false
    }
  },
  methods: {
    async login() {
      if (!this.email || !this.password) {
        service.show('请填写邮箱和密码', { type: 'warning' })
        return
      }
      this.loading = true
      try {
        const response = await apiService.login({ email: this.email, password: this.password })
        if (response && response.success) {
          service.show('登录成功', { type: 'success', duration: 800 })
          // use only is_admin flag returned by server
          const user = response.user
          saveUserToLocal(user);
          setTimeout(() => {
            if (user.is_admin) {
              this.$router.push('/admin/drivers')
            } else {
              this.$router.push('/main')
            }
          }, 700)
        } else {
          service.show(response && response.message ? response.message : '登录失败', { type: 'error' })
        }
      } catch (err) {
        service.show(err.response.data.message || '出现错误，联系网络或后端', { type: 'error' })
      } finally {
        this.loading = false
      }
    },
    
  }
}
</script>

<style scoped>
.login-container {
  width: 300px;
  padding: 20px;
  margin: 50px auto;
  border: 1px solid #ccc;
  border-radius: 10px;
  background-color: white;
  text-align: center;
}
input {
  width: 100%;
  padding: 8px;
  margin: 8px 0;
  box-sizing: border-box;
}
button {
  width: 100%;
  padding: 10px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
.links {
  margin-top: 10px;
  font-size: 14px;
}
.links a {
  color: #007BFF;
  text-decoration: none;
  margin: 0 5px;
}
</style>
