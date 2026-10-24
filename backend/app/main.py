"""FastAPI 应用入口。"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import init_db
from .routers import auth, chat, conversations, kb


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

# 允许前端跨域访问（开发阶段放开，生产可收紧）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["会话"])
app.include_router(kb.router, prefix="/api/kb", tags=["知识库"])
app.include_router(chat.router, prefix="/api", tags=["问答"])


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "llm_model": settings.llm_model,
        "embedding_model": settings.embedding_model,
        "has_api_key": bool(settings.dashscope_api_key),
    }
