import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.sqlite_store import get_db_path
from memory.qdrant_store import get_client, get_collection_name
from qdrant_client.models import Distance, VectorParams

# 清空SQLite
conn = sqlite3.connect(get_db_path())
conn.execute('DELETE FROM user_facts')
conn.execute('DELETE FROM users')
conn.execute('DELETE FROM episodes')
conn.commit()
conn.close()
print('SQLite记忆库已清空')

# 重置Qdrant
client = get_client()
col = get_collection_name()
client.delete_collection(col)
client.create_collection(col, vectors_config=VectorParams(size=1024, distance=Distance.COSINE))
print('向量库已重置')