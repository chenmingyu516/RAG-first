"""会话与历史消息管理。"""
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..deps import get_current_user, get_db
from ..models import Conversation, Message, User
from ..schemas import ConversationCreate, ConversationOut, MessageOut, RenameIn

router = APIRouter()


@router.get("", response_model=list[ConversationOut])
def list_conversations(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    convs = (
        db.query(Conversation)
        .filter(Conversation.user_id == user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )
    return convs


@router.post("", response_model=ConversationOut, status_code=status.HTTP_201_CREATED)
def create_conversation(
    data: ConversationCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = Conversation(user_id=user.id, title=(data.title or "新会话")[:100])
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


@router.get("/{conv_id}/messages", response_model=list[MessageOut])
def get_messages(
    conv_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = _get_own_conversation(conv_id, user, db)
    msgs = (
        db.query(Message)
        .filter(Message.conversation_id == conv.id)
        .order_by(Message.id.asc())
        .all()
    )
    return [_to_message_out(m) for m in msgs]


@router.patch("/{conv_id}", response_model=ConversationOut)
def rename_conversation(
    conv_id: int,
    data: RenameIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = _get_own_conversation(conv_id, user, db)
    conv.title = data.title
    conv.updated_at = datetime.now()
    db.commit()
    db.refresh(conv)
    return conv


@router.delete("/{conv_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conv_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = _get_own_conversation(conv_id, user, db)
    db.delete(conv)
    db.commit()


def _get_own_conversation(conv_id: int, user: User, db: Session) -> Conversation:
    conv = db.get(Conversation, conv_id)
    if conv is None or conv.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "会话不存在")
    return conv


def _to_message_out(m: Message) -> MessageOut:
    sources = None
    if m.sources:
        try:
            sources = json.loads(m.sources)
        except json.JSONDecodeError:
            sources = None
    return MessageOut(
        id=m.id, role=m.role, content=m.content, sources=sources, created_at=m.created_at
    )
