from langchain_chroma import Chroma
from app.model_provider import embeddings
from app.config import settings
def build_vector_store(chunks, persist_dir=settings.chroma_absolute_path):
    """传入切分好的chunks，构建向量库并持久化"""
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    return db

def load_vector_store(persist_dir=settings.chroma_absolute_path):
    """加载已经建好的本地向量库，不用重新embedding"""
    db = Chroma(
        embedding_function=embeddings,
        persist_directory=persist_dir
    )
    return db

if __name__ == "__main__":
     from app.rag.loader import load_pdf
     from app.rag.splitter import split_text
     docs = load_pdf()
     chunks = split_text(docs)
     print("向量库构建开始")
     db = build_vector_store(chunks)
     print("向量库构建完成")