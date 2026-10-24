"""知识库问答：SSE 流式返回，先发来源、再发答案。"""
import asyncio
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..deps import get_current_user, get_db
from ..models import Conversation, Message, User
from ..rag.chain import build_messages, format_context, retrieve
from ..rag.llm import get_llm
from ..schemas import ChatIn

router = APIRouter()

# 取最近 N 轮历史，控制上下文长度
HISTORY_TURNS = 6


def _sse(event: str, data) -> str:
    # 统一用 JSON 编码，字符串也会被正确引号包裹，避免数字等被误解析
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/chat")
async def chat(
    payload: ChatIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    question = payload.message.strip()
    if not question:
        raise HTTPException(400, "消息不能为空")

    # 1) 获取或新建会话
    conv = None
    if payload.conversation_id:
        conv = db.get(Conversation, payload.conversation_id)
        if conv is None or conv.user_id != user.id:
            raise HTTPException(404, "会话不存在")
    if conv is None:
        conv = Conversation(user_id=user.id, title=question[:20])
        db.add(conv)
        db.commit()
        db.refresh(conv)
    conv_id = conv.id

    # 2) 读取最近几轮历史（不含当前问题）
    history_rows = (
        db.query(Message)
        .filter(Message.conversation_id == conv_id)
        .order_by(Message.id.desc())
        .limit(HISTORY_TURNS)
        .all()
    )
    history = [{"role": m.role, "content": m.content} for m in reversed(history_rows)]

    # 3) 保存用户消息
    db.add(Message(conversation_id=conv_id, role="user", content=question))
    conv.updated_at = datetime.now()
    db.commit()

    async def event_stream():
        sources = []
        answer = ""
        try:
            # 检索知识库（网络调用放到线程池，避免阻塞）
            sources = await asyncio.to_thread(retrieve, question)
            yield _sse("sources", {"sources": sources})

            context = format_context(sources)
            messages = build_messages(history, question, context)

            async for chunk in get_llm().astream(messages):
                token = chunk.content if isinstance(chunk.content, str) else ""
                if token:
                    answer += token
                    yield _sse("token", token)

            # 保存助手消息
            db.add(
                Message(
                    conversation_id=conv_id,
                    role="assistant",
                    content=answer,
                    sources=json.dumps(sources, ensure_ascii=False),
                )
            )
            conv.updated_at = datetime.now()
            db.commit()
            yield _sse("done", {"conversation_id": conv_id})
        except Exception as e:  # noqa: BLE001
            yield _sse("error", {"message": f"生成回答失败：{e}"})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
