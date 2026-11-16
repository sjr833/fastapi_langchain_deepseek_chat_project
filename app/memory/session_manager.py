import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

def get_checkpointer() -> SqliteSaver:
    conn = sqlite3.connect("app/memory/checkpoint.db", check_same_thread=False)
    cp = SqliteSaver(conn)
    cp.setup()
    return cp
# 根据thread_id清空指定会话
def clear_thread(thread_id: str):
    cp = get_checkpointer()
    cp.delete_thread(thread_id)
    return {"ok": True, "message": f"会话 {thread_id} 已清除"}


