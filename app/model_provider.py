from langchain.chat_models import init_chat_model
from app.config import settings

# 初始化模型
model_chat = init_chat_model(
    model="deepseek-chat",
    api_key=settings.deepseek_api_key
)
model_summarize = init_chat_model(
    model="qwen3.8-flash",
    model_provider="openai",
    base_url=settings.dashscope_base_url,
    api_key=settings.dashscope_api_key
)