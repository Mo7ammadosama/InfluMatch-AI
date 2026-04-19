"""
WaslAI.jo — Embedding Engine
sentence-transformers: all-MiniLM-L6-v2
"""
from loguru import logger

_model = None


def get_embedding_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading embedding model: all-MiniLM-L6-v2")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed_text(text: str) -> list[float]:
    model = get_embedding_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def embed_influencer(influencer) -> str:
    text = (
        f"{influencer.display_name} {influencer.bio or ''} {influencer.bio_ar or ''} "
        f"categories: {' '.join(influencer.content_categories or [])} "
        f"city: {influencer.city} "
        f"languages: {' '.join(influencer.languages or [])} "
        f"followers: {influencer.total_followers} "
        f"engagement: {influencer.avg_engagement_rate}"
    )
    return text


def embed_campaign(campaign) -> str:
    text = (
        f"{campaign.title} {campaign.title_ar or ''} {campaign.description or ''} "
        f"categories: {' '.join(campaign.target_categories or [])} "
        f"platforms: {' '.join(campaign.required_platforms or [])} "
        f"budget: {campaign.total_budget_jod} JOD "
        f"cities: {' '.join(campaign.target_cities or [])}"
    )
    return text
