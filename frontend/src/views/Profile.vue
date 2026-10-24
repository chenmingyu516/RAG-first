<template>
  <div class="profile-page">
    <el-card class="profile-card">
      <div class="card-head">
        <el-button :icon="Back" @click="router.push('/chat')">返回</el-button>
        <h3 class="title">修改密码</h3>
      </div>
      <el-form label-width="90px" @submit.prevent="onSubmit">
        <el-form-item label="原密码">
          <el-input v-model="form.old_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input
            v-model="form.new_password"
            type="password"
            show-password
            placeholder="至少 6 位"
          />
        </el-form-item>
        <el-form-item label="确认新密码">
          <el-input
            v-model="form.confirm"
            type="password"
            show-password
            @keyup.enter="onSubmit"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="onSubmit">确认修改</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Back } from '@element-plus/icons-vue'
import { authApi } from '../api'
import { useAuthStore } from '../store'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const form = reactive({ old_password: '', new_password: '', confirm: '' })

async function onSubmit() {
  if (form.new_password.length < 6) {
    ElMessage.warning('新密码至少 6 位')
    return
  }
  if (form.new_password !== form.confirm) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  loading.value = true
  try {
    await authApi.changePassword({
      old_password: form.old_password,
      new_password: form.new_password,
    })
    ElMessage.success('密码修改成功，请重新登录')
    auth.logout()
    router.push('/login')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.profile-page {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}
.profile-card {
  width: 460px;
}
.card-head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.title {
  margin: 0;
  color: #303133;
}
</style>
