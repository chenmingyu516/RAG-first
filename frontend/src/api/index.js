import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const http = axios.create({ baseURL: '/api', timeout: 60000 })

http.interceptors.request.use((cfg) => {
  const t = localStorage.getItem('token')
  if (t) cfg.headers.Authorization = `Bearer ${t}`
  return cfg
})

http.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const status = err.response?.status
    const msg = err.response?.data?.detail || '请求失败'
    if (status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
    }
    ElMessage.error(typeof msg === 'string' ? msg : '请求失败')
    return Promise.reject(err)
  },
)

export const authApi = {
  register: (data) => http.post('/auth/register', data),
  login: (data) => http.post('/auth/login', data),
  me: () => http.get('/auth/me'),
  changePassword: (data) => http.post('/auth/change-password', data),
}

export const convApi = {
  list: () => http.get('/conversations'),
  create: (data) => http.post('/conversations', data),
  messages: (id) => http.get(`/conversations/${id}/messages`),
  remove: (id) => http.delete(`/conversations/${id}`),
}

export const kbApi = {
  list: () => http.get('/kb/documents'),
  upload: (file) => {
    const fd = new FormData()
    fd.append('file', file)
    return http.post('/kb/upload', fd)
  },
  remove: (id) => http.delete(`/kb/documents/${id}`),
}

/**
 * 问答流式请求（SSE）。events: sources / token / done / error
 */
export function chatStream(payload, { onSources, onToken, onDone, onError }) {
  const token = localStorage.getItem('token')
  return fetch('/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  }).then(async (resp) => {
    if (!resp.ok) {
      let msg = '请求失败'
      try {
        const j = await resp.json()
        msg = j.detail || msg
      } catch {
        /* ignore */
      }
      onError(msg)
      return
    }
    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buf = ''
    for (;;) {
      const { done, value } = await reader.read()
      if (done) break
      buf += decoder.decode(value, { stream: true })
      const blocks = buf.split('\n\n')
      buf = blocks.pop()
      for (const block of blocks) handleBlock(block, { onSources, onToken, onDone, onError })
    }
  })
}

function handleBlock(block, h) {
  let event = 'message'
  const dataLines = []
  for (const line of block.split('\n')) {
    if (line.startsWith('event:')) event = line.slice(6).trim()
    else if (line.startsWith('data:')) dataLines.push(line.slice(5).trim())
  }
  const raw = dataLines.join('')
  if (!raw) return
  let data = raw
  try {
    data = JSON.parse(raw)
  } catch {
    /* 保留原文 */
  }
  if (event === 'sources') h.onSources(data)
  else if (event === 'token') h.onToken(data)
  else if (event === 'done') h.onDone(data)
  else if (event === 'error') h.onError(data?.message || data)
}
