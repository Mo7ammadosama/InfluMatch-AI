from typing import List, Optional, Dict
from loguru import logger


class ARIAMatchingEngine:
    _model = None  # lazy-loaded SentenceTransformer
    _chroma_client = None

    SILVER_SCORE_THRESHOLD = 55.0
    MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

    def _get_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                ARIAMatchingEngine._model = SentenceTransformer(self.MODEL_NAME)
                logger.success(f"[ARIA::MATCHING] Model loaded: {self.MODEL_NAME}")
            except Exception as exc:
                logger.error(f"[ARIA::MATCHING] Cannot load embedding model: {exc}")
                raise
        return self._model

    def _get_chroma(self):
        if self._chroma_client is None:
            import chromadb
            from ...core.config import get_settings
            settings = get_settings()
            ARIAMatchingEngine._chroma_client = chromadb.PersistentClient(
                path=settings.chroma_persist_dir
            )
        return self._chroma_client

    def build_influencer_profile(self, influencer) -> str:
        platforms = []
        if getattr(influencer, "instagram_handle", None):
            platforms.append(f"instagram:{influencer.instagram_followers}")
        if getattr(influencer, "tiktok_handle", None):
            platforms.append(f"tiktok:{influencer.tiktok_followers}")
        if getattr(influencer, "youtube_handle", None):
            platforms.append(f"youtube:{influencer.youtube_subscribers}")

        bio = influencer.bio_ar or influencer.bio_en or ""
        return (
            f"{influencer.niche or ''} {influencer.city or ''} {bio} "
            f"platforms:{','.join(platforms)} score:{influencer.aria_score or 0}"
        ).strip()

    def build_influencer_profile_text(self, niche: str, city: str, aria_score: float) -> str:
        return f"{niche} {city} platforms:instagram score:{aria_score}".strip()

    async def index_all_influencers(self, db) -> int:
        from sqlalchemy import select
        from ...models.influencer import Influencer

        model = self._get_model()
        chroma = self._get_chroma()
        collection = chroma.get_or_create_collection("influencer_profiles")

        res = await db.execute(select(Influencer))
        influencers = res.scalars().all()

        if not influencers:
            logger.info("[ARIA::MATCHING] No influencers to index")
            return 0

        ids, docs, metas = [], [], []
        for inf in influencers:
            profile = self.build_influencer_profile(inf)
            ids.append(str(inf.id))
            docs.append(profile)
            metas.append({
                "influencer_id" : inf.id,
                "name"          : inf.instagram_handle or str(inf.id),
                "aria_score"    : inf.aria_score or 0.0,
                "aria_tier"     : inf.aria_tier or "UNRANKED",
                "city"          : inf.city or "",
                "niche"         : inf.niche or "",
            })

        embeddings = model.encode(docs).tolist()
        collection.upsert(ids=ids, documents=docs, embeddings=embeddings, metadatas=metas)
        logger.success(f"[ARIA::MATCHING] Indexed {len(influencers)} influencer profiles")
        return len(influencers)

    def match(self, campaign_brief: str, top_k: int = 10) -> List[Dict]:
        model  = self._get_model()
        chroma = self._get_chroma()

        try:
            collection = chroma.get_collection("influencer_profiles")
        except Exception:
            logger.warning("[ARIA::MATCHING] Collection 'influencer_profiles' not found — run index_all_influencers first")
            return []

        embedding = model.encode([campaign_brief]).tolist()
        results   = collection.query(
            query_embeddings = embedding,
            n_results        = min(top_k * 2, max(collection.count(), 1)),
            include          = ["metadatas", "distances"],
        )

        candidates = []
        metadatas  = results.get("metadatas", [[]])[0]
        distances  = results.get("distances", [[]])[0]

        for meta, dist in zip(metadatas, distances):
            aria_score = float(meta.get("aria_score", 0))
            if aria_score < self.SILVER_SCORE_THRESHOLD:
                continue
            similarity   = round(1.0 - dist, 4)
            final_score  = round(0.6 * similarity + 0.4 * (aria_score / 100), 4)
            candidates.append({
                "influencer_id" : meta.get("influencer_id"),
                "name"          : meta.get("name"),
                "aria_score"    : aria_score,
                "aria_tier"     : meta.get("aria_tier"),
                "similarity"    : similarity,
                "final_score"   : final_score,
                "city"          : meta.get("city"),
                "niche"         : meta.get("niche"),
            })

        candidates.sort(key=lambda x: x["final_score"], reverse=True)
        return candidates[:top_k]
