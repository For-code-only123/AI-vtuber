from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import yaml
import uuid

# 全局单例，只初始化一次
_client = None
_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("BAAI/bge-m3")
    return _embedder

def get_client():
    global _client
    if _client is None:
        with open("config.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        _client = QdrantClient(
            host=config["qdrant"]["host"],
            port=config["qdrant"]["port"]
        )
    return _client

def get_collection_name():
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config["qdrant"]["collection"]

def init_collection():
    client = get_client()
    col_name = get_collection_name()
    collections = [c.name for c in client.get_collections().collections]
    if col_name not in collections:
        client.create_collection(
            collection_name=col_name,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
        )
        print(f"集合 {col_name} 创建成功")
    else:
        print(f"集合 {col_name} 已存在")

def add_memory(text: str, metadata: dict):
    client = get_client()
    embedder = get_embedder()
    col_name = get_collection_name()
    vector = embedder.encode(text).tolist()
    point = PointStruct(
        id=str(uuid.uuid4()),
        vector=vector,
        payload={"text": text, **metadata}
    )
    client.upsert(collection_name=col_name, points=[point])

def search_memory(query: str, top_k: int = 3) -> list:
    client = get_client()
    embedder = get_embedder()
    col_name = get_collection_name()
    vector = embedder.encode(query).tolist()
    results = client.query_points(
        collection_name=col_name,
        query=vector,
        limit=top_k
    )
    return [r.payload for r in results.points]