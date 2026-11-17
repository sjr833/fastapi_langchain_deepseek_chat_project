from langchain.agents import create_agent
from app.memory.langgraph_sqlite_memory import checkpointer
from app.memory.summarize_middleware import middleware
from app.model_provider import model_chat
from app.prompts import system_prompt
from app.rag.retrieve_tool import os_rag_search
# 使用创建好的model创建agent
agent = create_agent(
    model=model_chat,
    system_prompt=system_prompt,
    checkpointer=checkpointer,
    middleware=[middleware],
    tools=[os_rag_search]
)











