<template>
  <div class="login-container">
    <h2>登录</h2>
    <input type="email" v-model="email" placeholder="邮箱">
    <input type="password" v-model="password" placeholder="密码">
    <button @click="login" :disabled="loading">{{ loading ? '登录中...' : '登录' }}</button>
    <div class="links">
      <a href="#" @click.prevent="forgot">忘记密码</a>|
      <a href="#" @click.prevent="register">注册</a>
    </div>
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
    displayMessage(type, text, duration = 3000) {
      service.show(text, { type, duration })
    },
    async login() {
      if (!this.email || !this.password) {
        this.displayMessage('warning', '请填写邮箱和密码')
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
        service.show('登录请求失败，请检查网络或后端', { type: 'error' })
      } finally {
        this.loading = false
      }
    },
    forgot() {
      service.showModal('功能未实现', { type: 'info' })
    },
    register() {
      service.showModal('功能未实现', { type: 'info' })
    },
    async fakeLogin(email, password) {
      const users = [
        {email: '23371147@buaa.edu.cn', password: 'mawanxu20051016'},
        {email: 'admin', password: '123'}
      ]
      await new Promise(resolve => setTimeout(resolve, 500))
      const user = users.find(u => u.email === email && u.password === password)
      if (user) {
        return { success: true }
      } else {
        return { success: false, message: '邮箱或密码错误' }
      }
    }
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
