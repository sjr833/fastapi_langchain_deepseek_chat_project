from langchain.agents.middleware import SummarizationMiddleware
from app.model_provider import model_summarize
from app.prompts import summary_prompt
# 初始化总结消息中间件
middleware = SummarizationMiddleware(
    model=model_summarize,
    trigger=("messages", 20), #  触发时机，当消息数超过20时，进行总结
    keep=("messages", 4), #  保留最近的5条原始数据，其余历史压缩为摘要
    summary_prompt=summary_prompt
)







