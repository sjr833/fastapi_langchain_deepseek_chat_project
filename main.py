from fastapi import FastAPI
from app.schemas import Req
from app.agent.agent_service import agent
from app.memory.session_manager import clear_thread
from langchain.messages import HumanMessage
# 创建fastapi实例
app=FastAPI()

@app.post("/chat")
async def chat (req:Req):
    response=agent.invoke({
        "messages":[HumanMessage(content=req.prompt)]},
        config = {"configurable": {"thread_id": req.thread_id}}
    )
    return response

@app.post("/clear")
async def clear(thread_id:str):
    return clear_thread(thread_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)