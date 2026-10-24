"""全局配置：从 .env 文件读取，未配置时使用默认值。"""
import os
from pathlib import Path

from dotenv import load_dotenv

# backend 目录（即 .env 所在目录）
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    app_name: str = "企业级 RAG 知识库问答系统"

    # ---- 阿里云百炼（DashScope）----
    dashscope_api_key: str = os.getenv("DASHSCOPE_API_KEY", "")
    dashscope_base_url: str = os.getenv(
        "DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    dashscope_native_base_url: str = os.getenv(
        "DASHSCOPE_NATIVE_BASE_URL", "https://dashscope.aliyuncs.com/api/v1"
    )
    llm_model: str = os.getenv("LLM_MODEL", "qwen-plus")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-v2")

    # ---- 检索参数 ----
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    top_k: int = int(os.getenv("TOP_K", "4"))
    score_threshold: float = float(os.getenv("SCORE_THRESHOLD", "0.2"))

    # ---- 数据库与向量存储 ----
    database_url: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'rag.db'}"
    )
    chroma_dir: str = os.getenv("CHROMA_DIR", str(BASE_DIR / "chroma_db"))
    upload_dir: str = str(BASE_DIR / "uploads")

    # ---- 安全 ----
    jwt_secret: str = os.getenv("JWT_SECRET", "dev-secret-change-me")
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))

    # ---- 管理员 ----
    admin_username: str = os.getenv("ADMIN_USERNAME", "admin")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "123456")


settings = Settings()
