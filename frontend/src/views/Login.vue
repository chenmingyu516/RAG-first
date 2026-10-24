<template>
  <div class="auth-page">
    <el-card class="auth-card">
      <h2 class="auth-title">企业级 RAG 知识库问答系统</h2>
      <p class="auth-sub">基于 LangChain 的智能商品问答助手</p>
      <el-form @submit.prevent="onLogin">
        <el-form-item>
          <el-input
            v-model="form.username"
            size="large"
            placeholder="用户名"
            :prefix-icon="User"
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.password"
            size="large"
            type="password"
            placeholder="密码"
            show-password
            :prefix-icon="Lock"
            @keyup.enter="onLogin"
          />
        </el-form-item>
        <el-button
          type="primary"
          size="large"
          class="w100"
          :loading="loading"
          @click="onLogin"
        >
          登录
        </el-button>
      </el-form>
      <div class="auth-foot">
        还没有账号？<router-link to="/register">立即注册</router-link>
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
import { useAuthStore } from '../store'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const form = reactive({ username: '', password: '' })

async function onLogin() {
  if (!form.username || !form.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    const res = await authApi.login(form)
    auth.setAuth(res.access_token, res.user)
    ElMessage.success('登录成功')
    router.push('/chat')
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
