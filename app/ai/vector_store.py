"""
InfluMatch.jo — ChromaDB Vector Store
Persistent local vector DB for influencer/campaign RAG
"""
import chromadb
from loguru import logger
from app.config import settings
from app.ai.embeddings import embed_text

_client = None
_collections: dict = {}


def get_chroma_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        logger.info(f"ChromaDB initialized at: {settings.chroma_persist_dir}")
    return _client


def get_collection(name: str):
    global _collections
    if name not in _collections:
        client = get_chroma_client()
        _collections[name] = client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},
        )
    return _collections[name]


def upsert_influencer(influencer_id: str, text: str, metadata: dict):
    collection = get_collection(settings.chroma_collection_influencers)
    embedding = embed_text(text)
    collection.upsert(
        ids=[influencer_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[metadata],
    )
    logger.debug(f"Upserted influencer {influencer_id} to ChromaDB")


def upsert_campaign(campaign_id: str, text: str, metadata: dict):
    collection = get_collection(settings.chroma_collection_campaigns)
    embedding = embed_text(text)
    collection.upsert(
        ids=[campaign_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[metadata],
    )
    logger.debug(f"Upserted campaign {campaign_id} to ChromaDB")


def query_influencers(query_text: str, n_results: int = 10) -> list[dict]:
    collection = get_collection(settings.chroma_collection_influencers)
    embedding = embed_text(query_text)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=min(n_results, collection.count() or 1),
        include=["documents", "metadatas", "distances"],
    )
    matches = []
    for i, doc_id in enumerate(results["ids"][0]):
        matches.append({
            "id": doc_id,
            "document": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i],
            "similarity": round(1 - results["distances"][0][i], 4),
        })
    return matches
