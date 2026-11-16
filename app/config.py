import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
# 加载环境变量
load_dotenv()
class Settings(BaseSettings):
    deepseek_api_key:str=os.getenv("DEEPSEEK_API_KEY")
    dashscope_api_key:str=os.getenv("DASHSCOPE_API_KEY")
    dashscope_base_url:str=os.getenv("DASHSCOPE_BASE_URL")
settings=Settings()

