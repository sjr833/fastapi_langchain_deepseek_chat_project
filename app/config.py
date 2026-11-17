import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
# 加载环境变量
load_dotenv()
class Settings(BaseSettings):
    deepseek_api_key:str=os.getenv("DEEPSEEK_API_KEY")
    dashscope_api_key:str=os.getenv("DASHSCOPE_API_KEY")
    dashscope_base_url:str=os.getenv("DASHSCOPE_BASE_URL")
    mineru_token:str=os.getenv("MINERU_TOKEN")
    chroma_absolute_path:str=os.getenv("CHROMA_ABSOLUTE_PATH")
settings=Settings()
# pdf资源地址
# pdf太大，分成三份
pdf_list = [
    "../../resources/操作系统1.pdf",
    "../../resources/操作系统2.pdf",
    "../../resources/操作系统3.pdf"
]

