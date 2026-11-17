from langchain.chat_models import init_chat_model
from langchain_community.embeddings import DashScopeEmbeddings
from app.config import settings

# 聊天模型
model_chat = init_chat_model(
    model="deepseek-chat",
    api_key=settings.deepseek_api_key
)
# 总结模型
model_summarize = init_chat_model(
    model="qwen3.8-flash",
    model_provider="openai",
    base_url=settings.dashscope_base_url,
    api_key=settings.dashscope_api_key
)
# 向量化模型
embeddings = DashScopeEmbeddings(
        model="text-embedding-v3",
        dashscope_api_key=settings.dashscope_api_key
    )