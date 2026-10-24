"""检索 + 提示词构建（RAG 核心逻辑）。"""
import threading
import time

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from ..config import settings
from .vectorstore import get_vectorstore

SYSTEM_PROMPT = """你是某电商平台的专业客服助手，既能基于知识库专业回答商品问题，也能和用户自然闲聊。

请遵循以下规则：
1. 若下方【知识库内容】包含回答所需信息，必须优先基于知识库作答，并引用其中的具体信息（参数、价格、售后等）。
2. 若知识库内容不足以回答商品相关问题，如实说明"知识库中暂无该商品的更多信息"，不要编造具体参数、价格、售后等事实。
3. 若用户是在闲聊、问候、自我介绍，或问与商品无关的通用问题，可基于自身能力友好自然地回答，不必引用知识库。
4. 回答中不要提及"知识库""检索""文档"等内部实现细节。
5. 使用友好、专业的中文。

【知识库内容】
{context}
"""

class _TTLCache:
    """简单的带过期时间的内存缓存（用于缓存检索结果，减少重复调用）。"""

    def __init__(self, ttl: float = 300):
        self.ttl = ttl
        self._data: dict = {}
        self._lock = threading.Lock()

    def get(self, key: str):
        with self._lock:
            item = self._data.get(key)
            if item and item[1] > time.time():
                return item[0]
            return None

    def set(self, key: str, value):
        with self._lock:
            self._data[key] = (value, time.time() + self.ttl)


_retrieval_cache = _TTLCache(ttl=300)


def retrieve(query: str) -> list[dict]:
    """按问题检索最相关的知识片段，返回带分数的来源列表。"""
    cached = _retrieval_cache.get(query)
    if cached is not None:
        return cached

    vs = get_vectorstore()
    results = vs.similarity_search_with_relevance_scores(query, k=settings.top_k)

    sources = []
    for doc, score in results:
        if score < settings.score_threshold:
            continue
        sources.append(
            {
                "content": doc.page_content,
                "source": doc.metadata.get("source", "未知来源"),
                "chunk_index": doc.metadata.get("chunk_index", 0),
                "score": round(float(score), 4),
            }
        )

    _retrieval_cache.set(query, sources)
    return sources


def format_context(sources: list[dict]) -> str:
    if not sources:
        return "（知识库中未找到与该问题相关的内容）"
    parts = []
    for i, s in enumerate(sources, 1):
        parts.append(f"[参考{i}] 来源：{s['source']}\n{s['content']}")
    return "\n\n".join(parts)


def build_messages(history: list[dict], question: str, context: str) -> list:
    """组装给大模型的消息：系统提示 + 历史对话 + 当前问题。"""
    messages = [SystemMessage(content=SYSTEM_PROMPT.format(context=context))]
    for h in history:
        if h.get("role") == "assistant":
            messages.append(AIMessage(content=h["content"]))
        else:
            messages.append(HumanMessage(content=h["content"]))
    messages.append(HumanMessage(content=question))
    return messages
