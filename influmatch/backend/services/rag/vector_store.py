import chromadb
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict
from loguru import logger
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
from backend.core.config import get_settings

settings = get_settings()

class WaslAIVectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200,
            separators=["\n\n", "\n", ".", "\u060c", " "]
        )
        self._init_collections()

    def _init_collections(self):
        self.contracts_col = self.client.get_or_create_collection("smart_contracts")
        self.policies_col = self.client.get_or_create_collection("jordan_policies")
        self.campaigns_col = self.client.get_or_create_collection("campaign_knowledge")
        logger.success("[ARIA::RAG] Vector store initialized")

    def _get_collection(self, doc_type: str):
        return {"contract": self.contracts_col, "policy": self.policies_col, "campaign": self.campaigns_col}.get(doc_type, self.policies_col)

    def ingest_document(self, text: str, doc_type: str, metadata: Dict):
        chunks = self.splitter.split_text(text)
        embeddings = self.encoder.encode(chunks).tolist()
        collection = self._get_collection(doc_type)
        ids = [f"{doc_type}_{metadata.get('id','doc')}_{i}" for i in range(len(chunks))]
        collection.add(documents=chunks, embeddings=embeddings, ids=ids, metadatas=[metadata]*len(chunks))
        logger.success(f"[ARIA::RAG] Ingested {len(chunks)} chunks | {doc_type}")

    def rebuild_index(self):
        """Delete all collections and recreate them (admin use only)"""
        for name in ["smart_contracts", "jordan_policies", "campaign_knowledge"]:
            try:
                self.client.delete_collection(name)
            except Exception:
                pass
        self._init_collections()
        logger.success("[ARIA::RAG] All collections wiped and recreated")

    def semantic_search(self, query: str, doc_type: str, top_k: int = 5) -> List[Dict]:
        collection = self._get_collection(doc_type)
        count = collection.count()
        if count == 0:
            return []
        embedding = self.encoder.encode(query).tolist()
        results = collection.query(query_embeddings=[embedding], n_results=min(top_k, count))
        return [
            {"text": doc, "metadata": meta, "distance": dist}
            for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0])
        ]
