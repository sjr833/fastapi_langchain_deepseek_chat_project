from langchain.tools import tool
from app.rag.vector_store import load_vector_store
# 提前加载向量库，避免每次调用重复加载
vector_db = load_vector_store()
# 把向量库转为检索器
retriever = vector_db.as_retriever(search_kwargs={"k": 5})
@tool
def os_rag_search(query: str) -> str:
    """
    操作系统知识库检索工具。
    仅在用户提问和【操作系统】相关内容时使用该工具。
    从操作系统PDF资料中检索相关知识点、定义、原理、算法。
    Args:
        query: 用户的问题，用于检索知识库
    """
    docs = retriever.invoke(query)
    # 拼接检索结果
    context = "\n\n".join([d.page_content for d in docs])
    return context