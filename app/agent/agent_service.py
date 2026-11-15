from langchain.agents import create_agent
from app.schemas import Resp
from app.memory.langgraph_sqlite_memory import checkpointer
from app.memory.summarize_middleware import middleware
from app.model_provider import model_chat
from app.prompts import system_prompt
# 使用创建好的model创建agent
agent = create_agent(
    model=model_chat,
    system_prompt=system_prompt,
    response_format=Resp,
    checkpointer=checkpointer,
    middleware=[middleware]
)











