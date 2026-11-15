from pydantic import BaseModel,Field
# fastapi请求体参数类型
class Req(BaseModel):
    prompt:str=Field(...,min_length=1,max_length=4096,description="用户提问内容")

# 结构化输出格式
class Resp(BaseModel):
    content:str
