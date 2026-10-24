"""知识库管理（仅管理员）：上传、列表、删除文档。"""
import shutil
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..config import settings
from ..deps import get_current_admin, get_db
from ..models import Document
from ..rag.document_loader import SUPPORTED_EXTS, load_and_split
from ..rag.vectorstore import add_documents, delete_by_document_id

router = APIRouter()


class DocumentOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    filename: str
    chunk_count: int
    size: int
    created_at: datetime


@router.get("/documents", response_model=list[DocumentOut])
def list_documents(_=Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(Document).order_by(Document.id.desc()).all()


@router.post("/upload", response_model=DocumentOut, status_code=201)
async def upload(
    file: UploadFile, _=Depends(get_current_admin), db: Session = Depends(get_db)
):
    filename = file.filename or "未命名"
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_EXTS:
        raise HTTPException(400, f"不支持的文件类型，仅支持：{'、'.join(sorted(SUPPORTED_EXTS))}")

    # 先落盘到临时文件
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = upload_dir / f"{uuid.uuid4().hex}{ext}"
    size = 0
    with open(tmp_path, "wb") as f:
        while chunk := await file.read(1024 * 1024):
            f.write(chunk)
            size += len(chunk)

    # 记录文档元信息
    doc = Document(filename=filename, size=size)
    db.add(doc)
    db.commit()
    db.refresh(doc)

    try:
        chunks = load_and_split(tmp_path, filename, doc.id)
        add_documents(chunks)
        doc.chunk_count = len(chunks)
        db.commit()
        db.refresh(doc)
    except Exception as e:
        db.delete(doc)
        db.commit()
        raise HTTPException(500, f"文档解析失败：{e}")
    finally:
        tmp_path.unlink(missing_ok=True)

    return doc


@router.delete("/documents/{doc_id}", status_code=204)
def delete_document(
    doc_id: int, _=Depends(get_current_admin), db: Session = Depends(get_db)
):
    doc = db.get(Document, doc_id)
    if doc is None:
        raise HTTPException(404, "文档不存在")
    delete_by_document_id(doc.id)
    db.delete(doc)
    db.commit()
