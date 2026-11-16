import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
# 初始化checkpointer
checkpointer = SqliteSaver(sqlite3.connect("app/memory/checkpoint.db", check_same_thread=False))
# 自动建表
checkpointer.setup()
