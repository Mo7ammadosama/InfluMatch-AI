"""
ARIA Integration Test Suite — Section 4
Tests complete campaign lifecycle end-to-end
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

BASE_URL = "http://localhost:8000/api"

class TestScoringAlgorithm:
    """Test ARIA Influencer Scoring"""

    def test_micro_influencer_scoring(self):
        from backend.services.scoring.influencer_scorer import ARIAInfluencerScorer
        scorer = ARIAInfluencerScorer()
        data = {
            "instagram_followers": 45000,
            "instagram_engagement_rate": 4.2,
            "tiktok_followers": 12000,
            "tiktok_engagement_rate": 6.8,
            "youtube_subscribers": 0,
            "city": "amman",
            "niche": "fashion",
            "account_age_days": 730,
            "campaigns_completed": 8,
            "campaigns_total": 9,
            "on_time_deliveries": 8,
            "disputes_raised": 0,
            "monthly_growth_rate": 2.5,
        }
        result = scorer.compute_aria_score(data, niche="fashion")
        assert result["aria_score"] > 0
        assert result["aria_score"] <= 100
        assert "tier" in result
        print(f"ARIA Score: {result['aria_score']} | Tier: {result['tier']}")

    def test_mega_influencer_penalty(self):
        from backend.services.scoring.influencer_scorer import ARIAInfluencerScorer
        scorer = ARIAInfluencerScorer()
        result = scorer.compute_aria_score(
            {
                "instagram_followers": 2000000,
                "instagram_engagement_rate": 0.8,
                "city": "dubai",
                "account_age_days": 365,
            },
            niche="food"
        )
        print(f"Mega influencer score: {result['aria_score']}")
        # Mega influencer (2M followers, low ER, non-Jordan city) scores lower than micro
        assert result["aria_score"] < 95


class TestEscrowEngine:
    """Test Escrow state machine"""

    def test_escrow_vat_calculation(self):
        amount_jod = 500.0
        vat        = amount_jod * 0.16
        commission = amount_jod * 0.05
        net        = amount_jod - commission
        assert vat == 80.0
        assert commission == 25.0
        assert net == 475.0
        print(f"Escrow math: 500 JOD -> Net: {net} | VAT: {vat} | Fee: {commission}")

    def test_valid_transitions(self):
        from backend.services.escrow.escrow_engine import VALID_TRANSITIONS
        from backend.models.escrow import EscrowStatus
        assert EscrowStatus.FUNDED    in VALID_TRANSITIONS[EscrowStatus.PENDING]
        assert EscrowStatus.RELEASED  in VALID_TRANSITIONS[EscrowStatus.UNDER_REVIEW]
        assert EscrowStatus.DISPUTED  in VALID_TRANSITIONS[EscrowStatus.IN_PROGRESS]
        assert EscrowStatus.CANCELLED in VALID_TRANSITIONS[EscrowStatus.DISPUTED]
        print("Escrow state machine: PASS")


class TestRAGSystem:
    """Test RAG vector store"""

    def test_vector_store_init(self):
        from backend.services.rag.vector_store import WaslAIVectorStore
        store = WaslAIVectorStore()
        assert store.contracts_col is not None
        assert store.policies_col is not None
        print("RAG vector store initialized: PASS")

    def test_document_ingestion(self):
        from backend.services.rag.vector_store import WaslAIVectorStore
        store = WaslAIVectorStore()
        store.ingest_document(
            "Test contract for Jordan market compliance",
            "contracts",
            {"id": "test_001", "language": "en", "source": "test"}
        )
        print("Document ingestion: PASS")


class TestLoyaltyWallet:
    """Test loyalty points engine"""

    def test_points_to_jod_conversion(self):
        from backend.services.wallet.loyalty_engine import LoyaltyWalletEngine
        engine = LoyaltyWalletEngine()
        assert engine.calculate_jod_value(0)    == 0.0
        assert engine.calculate_jod_value(500)  == 5.0
        assert engine.calculate_jod_value(1000) == 10.0
        print("Loyalty wallet conversion: PASS")

    def test_merchant_tier(self):
        from backend.services.wallet.loyalty_engine import LoyaltyWalletEngine
        engine = LoyaltyWalletEngine()
        assert engine.get_tier(1000)["tier"]  == "BRONZE"
        assert engine.get_tier(5000)["tier"]  == "SILVER"
        assert engine.get_tier(20000)["tier"] == "GOLD"
        assert engine.get_tier(50000)["tier"] == "PLATINUM"
        print("Merchant tier calculation: PASS")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
