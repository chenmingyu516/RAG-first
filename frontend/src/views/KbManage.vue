<template>
  <el-container class="kb-page">
    <el-header class="header">
      <div class="header-left">
        <el-button :icon="Back" @click="router.push('/chat')">返回问答</el-button>
        <span class="title">知识库管理</span>
        <el-tag type="danger" effect="dark">仅管理员可见</el-tag>
      </div>
      <span class="user-chip">
        <el-icon><User /></el-icon>{{ user?.username }}
      </span>
    </el-header>

    <el-main class="main">
      <el-card class="upload-card" shadow="never">
        <template #header>
          <span>上传知识文档（商品资料）</span>
        </template>
        <el-upload
          drag
          multiple
          :http-request="doUpload"
          :show-file-list="true"
          accept=".pdf,.docx,.txt,.md"
        >
          <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
          <div class="el-upload__text">拖拽文件到此处，或 <em>点击上传</em></div>
          <template #tip>
            <div class="el-upload__tip">
              支持 PDF / Word / TXT / Markdown。上传后系统会自动分块并建立检索索引。
            </div>
          </template>
        </el-upload>
      </el-card>

      <el-card class="list-card" shadow="never">
        <template #header>
          <div class="list-header">
            <span>已上传文档（共 {{ docs.length }} 个）</span>
            <el-button size="small" :icon="Refresh" @click="loadDocs">刷新</el-button>
          </div>
        </template>
        <el-table :data="docs" v-loading="loading">
          <el-table-column prop="id" label="ID" width="70" />
          <el-table-column prop="filename" label="文件名" min-width="220" show-overflow-tooltip />
          <el-table-column prop="chunk_count" label="分块数" width="100" />
          <el-table-column label="大小" width="120">
            <template #default="{ row }">{{ formatSize(row.size) }}</template>
          </el-table-column>
          <el-table-column label="上传时间" width="180">
            <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button type="danger" size="small" @click="delDoc(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </el-main>
  </el-container>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Back, Refresh, UploadFilled, User } from '@element-plus/icons-vue'
import { kbApi } from '../api'
import { useAuthStore } from '../store'

const router = useRouter()
const auth = useAuthStore()
const user = computed(() => auth.user)

const docs = ref([])
const loading = ref(false)

async function loadDocs() {
  loading.value = true
  try {
    docs.value = await kbApi.list()
  } finally {
    loading.value = false
  }
}

async function doUpload(options) {
  try {
    const res = await kbApi.upload(options.file)
    ElMessage.success(`「${options.file.name}」上传成功`)
    loadDocs()
    options.onSuccess(res)
  } catch (e) {
    options.onError(e)
  }
}

async function delDoc(row) {
  try {
    await ElMessageBox.confirm(
      `确定删除「${row.filename}」吗？删除后其知识片段将无法再被检索到。`,
      '提示',
      { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' },
    )
  } catch {
    return
  }
  await kbApi.remove(row.id)
  ElMessage.success('删除成功')
  loadDocs()
}

function formatSize(n) {
  if (!n) return '0 B'
  if (n < 1024) return n + ' B'
  if (n < 1024 * 1024) return (n / 1024).toFixed(1) + ' KB'
  return (n / 1024 / 1024).toFixed(2) + ' MB'
}

function formatTime(t) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
}

onMounted(() => {
  loadDocs()
})
</script>

<style scoped>
.kb-page {
  height: 100%;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.title {
  font-size: 17px;
  font-weight: 600;
  color: #303133;
}
.user-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #606266;
  font-size: 14px;
}
.main {
  background: #f5f7fa;
  padding: 16px;
  max-width: 1000px;
  margin: 0 auto;
  width: 100%;
}
.upload-card,
.list-card {
  margin-bottom: 16px;
}
.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
