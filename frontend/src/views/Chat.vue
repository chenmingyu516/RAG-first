<template>
  <el-container class="chat-page">
    <el-aside width="260px" class="sidebar">
      <div class="sidebar-header">
        <el-button type="primary" :icon="Plus" class="new-btn" @click="newChat">
          新建会话
        </el-button>
      </div>
      <div class="conv-list">
        <div
          v-for="c in conversations"
          :key="c.id"
          class="conv-item"
          :class="{ active: c.id === currentId }"
          @click="selectConv(c.id)"
        >
          <div class="conv-title" :title="c.title">{{ c.title }}</div>
          <el-icon class="conv-del" @click.stop="delConv(c.id)"><Delete /></el-icon>
        </div>
        <el-empty
          v-if="!conversations.length"
          description="暂无会话"
          :image-size="60"
        />
      </div>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-title">{{ currentTitle }}</div>
        <el-dropdown @command="onCommand">
          <span class="user-chip">
            <el-icon><User /></el-icon>
            <span class="user-name">{{ user?.username }}</span>
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">修改密码</el-dropdown-item>
              <el-dropdown-item v-if="isAdmin" command="kb">知识库管理</el-dropdown-item>
              <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>

      <el-main class="main">
        <div ref="msgListRef" class="msg-list">
          <el-empty
            v-if="!messages.length"
            description="开始提问吧，例如：这款手机支持快充吗？"
          />
          <div v-for="(m, idx) in messages" :key="idx" class="msg" :class="m.role">
            <div class="bubble">
              <div
                v-if="m.role === 'assistant'"
                class="md"
                v-html="renderMd(m.content || (m.streaming ? '正在思考…' : ''))"
              ></div>
              <div v-else class="text">{{ m.content }}</div>

              <el-collapse
                v-if="m.role === 'assistant' && m.sources && m.sources.length"
                class="sources"
              >
                <el-collapse-item :title="`📚 参考来源（${m.sources.length} 条知识片段）`">
                  <div v-for="(s, i) in m.sources" :key="i" class="source-item">
                    <div class="source-head">
                      <span class="source-name">{{ i + 1 }}. {{ s.source }}</span>
                      <el-tag size="small" type="info">
                        相关度 {{ Math.round((s.score || 0) * 100) }}%
                      </el-tag>
                    </div>
                    <div class="source-content">{{ s.content }}</div>
                  </div>
                </el-collapse-item>
              </el-collapse>
            </div>
          </div>
        </div>
      </el-main>

      <el-footer class="footer">
        <div class="input-box">
          <el-input
            v-model="input"
            type="textarea"
            :rows="3"
            resize="none"
            placeholder="请输入你的问题，Enter 发送 / Shift+Enter 换行"
            @keydown="onKeydown"
          />
          <el-button
            type="primary"
            class="send-btn"
            :icon="Promotion"
            :loading="streaming"
            :disabled="!input.trim()"
            @click="send"
          >
            发送
          </el-button>
        </div>
      </el-footer>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Promotion, Delete, User, ArrowDown } from '@element-plus/icons-vue'
import { chatStream, convApi } from '../api'
import { useAuthStore } from '../store'
import { renderMarkdown } from '../utils/markdown'

const router = useRouter()
const auth = useAuthStore()
const user = computed(() => auth.user)
const isAdmin = computed(() => auth.isAdmin)

const conversations = ref([])
const currentId = ref(null)
const messages = ref([])
const input = ref('')
const streaming = ref(false)
const msgListRef = ref(null)

const currentTitle = computed(() => {
  const c = conversations.value.find((x) => x.id === currentId.value)
  return c ? c.title : '新会话'
})

function renderMd(text) {
  return renderMarkdown(text)
}

async function loadConversations() {
  conversations.value = await convApi.list()
}

function newChat() {
  if (streaming.value) return
  currentId.value = null
  messages.value = []
}

async function selectConv(id) {
  if (streaming.value || id === currentId.value) return
  currentId.value = id
  messages.value = await convApi.messages(id)
  scrollBottom()
}

async function delConv(id) {
  try {
    await ElMessageBox.confirm('确定删除该会话及其全部记录吗？', '提示', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }
  await convApi.remove(id)
  if (currentId.value === id) {
    currentId.value = null
    messages.value = []
  }
  loadConversations()
}

function onKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    send()
  }
}

async function send() {
  const text = input.value.trim()
  if (!text || streaming.value) return
  input.value = ''

  messages.value.push({ role: 'user', content: text })
  const aiIndex = messages.value.length
  messages.value.push({ role: 'assistant', content: '', sources: [], streaming: true })
  streaming.value = true
  scrollBottom()

  const convIdAtStart = currentId.value

  await chatStream(
    { conversation_id: convIdAtStart, message: text },
    {
      onSources(data) {
        messages.value[aiIndex].sources = data.sources || []
      },
      onToken(t) {
        messages.value[aiIndex].content += t
        scrollBottom()
      },
      onDone(d) {
        messages.value[aiIndex].streaming = false
        streaming.value = false
        if (!convIdAtStart && d.conversation_id) currentId.value = d.conversation_id
        loadConversations()
        scrollBottom()
      },
      onError(msg) {
        messages.value[aiIndex].streaming = false
        if (!messages.value[aiIndex].content) {
          messages.value[aiIndex].content = '（生成失败，请稍后重试）'
        }
        streaming.value = false
        ElMessage.error(typeof msg === 'string' ? msg : '生成失败')
        loadConversations()
      },
    },
  )
}

function scrollBottom() {
  nextTick(() => {
    if (msgListRef.value) {
      msgListRef.value.scrollTop = msgListRef.value.scrollHeight
    }
  })
}

function onCommand(cmd) {
  if (cmd === 'profile') router.push('/profile')
  else if (cmd === 'kb') router.push('/kb')
  else if (cmd === 'logout') {
    auth.logout()
    router.push('/login')
  }
}

onMounted(() => {
  loadConversations()
})
</script>

<style scoped>
.chat-page {
  height: 100%;
}
.sidebar {
  background: #1d2530;
  color: #fff;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.sidebar-header {
  padding: 14px;
}
.new-btn {
  width: 100%;
}
.conv-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 8px 12px;
}
.conv-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  margin-bottom: 4px;
  border-radius: 8px;
  cursor: pointer;
  color: #cfd3da;
  transition: background 0.15s;
}
.conv-item:hover {
  background: rgba(255, 255, 255, 0.08);
}
.conv-item.active {
  background: #2f6fed;
  color: #fff;
}
.conv-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
}
.conv-del {
  opacity: 0;
  transition: opacity 0.15s;
}
.conv-item:hover .conv-del {
  opacity: 1;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
}
.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}
.user-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  color: #303133;
  font-size: 14px;
  outline: none;
}
.main {
  padding: 16px;
  background: #f5f7fa;
}
.msg-list {
  height: 100%;
  overflow-y: auto;
  max-width: 860px;
  margin: 0 auto;
}
.msg {
  display: flex;
  margin-bottom: 16px;
}
.msg.user {
  justify-content: flex-end;
}
.msg.assistant {
  justify-content: flex-start;
}
.bubble {
  max-width: 78%;
  padding: 10px 14px;
  border-radius: 10px;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}
.msg.user .bubble {
  background: #2f6fed;
  color: #fff;
}
.msg.user .text {
  color: #fff;
  white-space: pre-wrap;
  word-break: break-word;
}
.sources {
  margin-top: 10px;
  border: none;
}
.source-item {
  border-bottom: 1px dashed #ebeef5;
  padding: 6px 0;
}
.source-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 4px;
}
.source-name {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}
.source-content {
  font-size: 12.5px;
  color: #909399;
  background: #f8f9fb;
  padding: 8px 10px;
  border-radius: 6px;
  max-height: 120px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
}
.footer {
  background: #fff;
  border-top: 1px solid #ebeef5;
  padding: 12px 16px;
  height: auto;
}
.input-box {
  max-width: 860px;
  margin: 0 auto;
  display: flex;
  gap: 10px;
  align-items: flex-end;
}
.send-btn {
  height: 76px;
  width: 90px;
}
</style>
