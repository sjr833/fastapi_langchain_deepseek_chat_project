from fastapi import FastAPI
from app.schemas import Req
from app.agent.agent_service import agent
from langchain.messages import HumanMessage
from app.config import config
# 创建fastapi实例
app=FastAPI()

@app.post("/chat")
async def chat_(req:Req):
    response=agent.invoke({
        "messages":[HumanMessage(content=req.prompt)]},
        config
    )
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)