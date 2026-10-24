"""大模型与嵌入模型（阿里云百炼，走 OpenAI 兼容接口）。"""
from functools import lru_cache

from langchain_community.embeddings import DashScopeEmbeddings
from langchain_openai import ChatOpenAI

from ..config import settings


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    """问答用的大模型，流式输出。"""
    return ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.dashscope_api_key,
        base_url=settings.dashscope_base_url,
        temperature=0.3,
        streaming=True,
    )


@lru_cache(maxsize=1)
def get_embeddings() -> DashScopeEmbeddings:
    """把文字转成向量的嵌入模型（走阿里云百炼原生嵌入接口）。"""
    import dashscope

    # 使用工作空间专属的原生接口地址
    dashscope.base_http_api_url = settings.dashscope_native_base_url
    return DashScopeEmbeddings(
        model=settings.embedding_model,
        dashscope_api_key=settings.dashscope_api_key,
    )
