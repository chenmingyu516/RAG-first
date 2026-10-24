<template>
  <div class="auth-page">
    <el-card class="auth-card">
      <h2 class="auth-title">注册账号</h2>
      <p class="auth-sub">注册后即可使用知识库问答</p>
      <el-form @submit.prevent="onRegister">
        <el-form-item>
          <el-input
            v-model="form.username"
            size="large"
            placeholder="用户名（3-30 位）"
            :prefix-icon="User"
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.password"
            size="large"
            type="password"
            placeholder="密码（至少 6 位）"
            show-password
            :prefix-icon="Lock"
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.confirm"
            size="large"
            type="password"
            placeholder="确认密码"
            show-password
            :prefix-icon="Lock"
            @keyup.enter="onRegister"
          />
        </el-form-item>
        <el-button
          type="primary"
          size="large"
          class="w100"
          :loading="loading"
          @click="onRegister"
        >
          注册
        </el-button>
      </el-form>
      <div class="auth-foot">
        已有账号？<router-link to="/login">去登录</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { authApi } from '../api'

const router = useRouter()
const loading = ref(false)
const form = reactive({ username: '', password: '', confirm: '' })

async function onRegister() {
  if (form.password !== form.confirm) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  loading.value = true
  try {
    await authApi.register({ username: form.username, password: form.password })
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1f6feb 0%, #6aa1ff 100%);
}
.auth-card {
  width: 400px;
  padding: 10px 8px;
}
.auth-title {
  margin: 0;
  text-align: center;
  color: #303133;
}
.auth-sub {
  margin: 8px 0 24px;
  text-align: center;
  color: #909399;
  font-size: 13px;
}
.w100 {
  width: 100%;
}
.auth-foot {
  margin-top: 16px;
  text-align: center;
  font-size: 14px;
  color: #909399;
}
</style>
