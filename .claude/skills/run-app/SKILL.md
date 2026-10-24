---
name: run-app
description: 启动「RAG 知识库问答系统」，打开网页查看运行效果
---

# 启动 RAG 知识库问答系统

本技能用于启动这个 RAG 问答系统（FastAPI 后端 + Vue 前端），让用户能在浏览器里使用。

## 启动方式（二选一）

### 方式 A：一键启动（Windows 推荐）

在项目根目录双击（或运行）`start.bat`，会自动打开两个窗口：

- `RAG Backend`：后端，地址 http://127.0.0.1:8000
- `RAG Frontend`：前端，地址 http://localhost:5173

### 方式 B：手动启动

```bash
# 后端（在 backend 目录）
cd backend && .venv/Scripts/python.exe run.py

# 前端（另开一个终端，在 frontend 目录）
cd frontend && npm run dev
```

## 验证是否启动成功

- 后端：浏览器打开 http://127.0.0.1:8000/api/health 应返回 JSON（含 `status: ok`）。
- 前端：浏览器打开 http://localhost:5173 能看到登录页。

## 重要注意事项

- 后端依赖在 `backend/.venv`，前端依赖在 `frontend/node_modules`；首次运行前确保已执行过 `setup.bat`。
- 后端需要在 `backend/.env` 里填好 `DASHSCOPE_API_KEY`，否则问答会报错。
- 若提示端口被占用，先关闭之前已启动的窗口再重试。
- 用中文告知用户：系统已启动，请用浏览器打开 http://localhost:5173（管理员 admin / 123456）。
