from pydantic import BaseModel,Field
# fastapi请求体参数类型
class Req(BaseModel):
    prompt:str=Field(...,min_length=1,max_length=4096,description="用户提问内容")
    thread_id:str=Field(default="001",min_length=1,max_length=10,description="会话主键")


