"""Chroma 向量库：知识的存储与检索。"""
import threading

from langchain_chroma import Chroma

from ..config import settings
from .llm import get_embeddings

_vectorstore = None
_lock = threading.Lock()


def get_vectorstore() -> Chroma:
    """懒加载全局唯一的向量库实例（余弦相似度）。"""
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = Chroma(
            collection_name="knowledge_base",
            embedding_function=get_embeddings(),
            persist_directory=settings.chroma_dir,
            collection_metadata={"hnsw:space": "cosine"},
        )
    return _vectorstore


def add_documents(docs: list) -> None:
    with _lock:
        get_vectorstore().add_documents(docs)


def delete_by_document_id(document_id: int) -> None:
    with _lock:
        get_vectorstore().delete(where={"document_id": document_id})
