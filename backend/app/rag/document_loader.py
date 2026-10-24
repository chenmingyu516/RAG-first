"""文档解析与分块：把上传的商品资料切成适合检索的小片段。"""
from pathlib import Path

from langchain_community.document_loaders import (
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

from ..config import settings

SUPPORTED_EXTS = {".pdf", ".docx", ".txt", ".md"}


def _load(path: Path) -> list:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return PyPDFLoader(str(path)).load()
    if ext == ".docx":
        return Docx2txtLoader(str(path)).load()
    # txt / md 统一按文本读取
    return TextLoader(str(path), encoding="utf-8").load()


def load_and_split(path: Path, filename: str, document_id: int) -> list:
    """读取文件并切成 chunk，每个 chunk 带上来源元信息。"""
    raw_docs = _load(path)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", "。", "！", "？", "；", ".", "!", "?", ";", " ", ""],
    )
    chunks = splitter.split_documents(raw_docs)

    for i, c in enumerate(chunks):
        c.metadata["source"] = filename
        c.metadata["document_id"] = document_id
        c.metadata["chunk_index"] = i

    return chunks
