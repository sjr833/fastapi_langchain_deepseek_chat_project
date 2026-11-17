from langchain_mineru import MinerULoader
from app.config import settings,pdf_list
def load_pdf():
    # 存储加载的pdf
    all_docs = []
    # 循环加载
    print("加载开始！")
    for fp in pdf_list:
        loader = MinerULoader(
            source=fp,
            mode="precision", # 可选: flash 、 precision
            ocr=True,    # 对于扫描件类型的PDF，MinerU处理起来也毫不费力，只需要把OCR参数改为True即可
            token=settings.mineru_token
        )
        print(f"{fp}正在加载")
        #  解析文档，返回值直接是LangChain的 Document集合(列表)
        docs = loader.load()
        print(f"{fp}加载完成")
        all_docs.extend(docs)
    print("加载完毕！")
    return all_docs


if __name__ == "__main__":
     docs = load_pdf()
     print(f"一共加载文档片段数：{len(docs)}")
     if docs:
         print("====第一条文档预览====")
         print(docs[0].page_content[:300])