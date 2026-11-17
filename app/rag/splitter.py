from langchain_text_splitters import RecursiveCharacterTextSplitter
# 创建递归切分器
recursive_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=120,
    separators=["\n\n", "\n", "。","，"]  # 优先级从高到低
)
def split_text(docs):
    print("切分开始！")
    chunks=recursive_splitter.split_documents(docs)
    print("切分完毕！")
    return chunks

if __name__ == "__main__":
     from app.rag.loader import load_pdf
     docs = load_pdf()
     chunks = split_text(docs)
     print(f"切分后chunk总数：{len(chunks)}")
     if chunks:
         print("====第一个chunk预览====")
         print(chunks[0].page_content[:300])