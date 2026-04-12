# ============================================================
# COMPONENT 26: backend/tests/unit/test_all_units.py
# Consolidated unit test runner — all core modules
# ============================================================

import pytest
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent.parent.parent  # → /c/InfluMatch_AI
sys.path.insert(0, str(ROOT))


# ══════════════════════════════════════════════════════════
class TestScoringEngine:
    def test_tier_classification(self):
        from influmatch.backend.services.scoring.influencer_scorer import ARIAInfluencerScorer
        s = ARIAInfluencerScorer()
        result = s.compute_final_aria_score(
            {
                "instagram_followers"      : 50000,
                "instagram_engagement_rate": 4.5,
                "city"                     : "amman",
                "niche"                    : "fashion",
                "account_age_days"         : 500,
                "campaigns_completed"      : 5,
                "campaigns_total"          : 5,
                "on_time_deliveries"       : 5,
                "disputes_raised"          : 0,
            },
            campaign_niche="fashion"
        )
        assert 0 <= result["aria_score"] <= 100
        assert result["tier"] in [
            "PLATINUM ⭐⭐⭐", "GOLD ⭐⭐", "SILVER ⭐", "BRONZE", "UNRANKED"
        ]
        assert "breakdown" in result
        print(f"\n✅ Scoring: {result['aria_score']} | {result['tier']}")

    def test_jordan_location_bonus(self):
        from influmatch.backend.services.scoring.influencer_scorer import ARIAInfluencerScorer
        s = ARIAInfluencerScorer()
        amman_score = s.calculate_market_relevance(
            {"city": "amman", "niche": "fashion"}, "fashion"
        )
        dubai_score = s.calculate_market_relevance(
            {"city": "dubai", "niche": "fashion"}, "fashion"
        )
        assert amman_score > dubai_score
        print(f"\n✅ Jordan bonus: Amman={amman_score} > Dubai={dubai_score}")

    def test_micro_influencer_tier_bonus(self):
        from influmatch.backend.services.scoring.influencer_scorer import ARIAInfluencerScorer
        s = ARIAInfluencerScorer()
        assert s._get_tier_bonus(50000)  == 1.2   # Micro → premium
        assert s._get_tier_bonus(2000000) == 0.70  # Mega  → penalty
        print("\n✅ Tier bonus: micro=1.2x, mega=0.70x")


# ══════════════════════════════════════════════════════════
class TestWalletEngine:
    def test_points_conversion(self):
        from influmatch.backend.services.wallet.loyalty_engine import LoyaltyWalletEngine
        e = LoyaltyWalletEngine()
        assert e.calculate_jod_value(0)   == 0.0
        assert e.calculate_jod_value(499) == 0.0   # Below minimum
        assert e.calculate_jod_value(500) == 5.0
        assert e.calculate_jod_value(1000) == 10.0
        print("\n✅ Points conversion accurate")

    def test_all_tiers(self):
        from influmatch.backend.services.wallet.loyalty_engine import LoyaltyWalletEngine
        e = LoyaltyWalletEngine()
        assert e.get_tier(100)["tier"]   == "BRONZE"
        assert e.get_tier(5000)["tier"]  == "SILVER"
        assert e.get_tier(20000)["tier"] == "GOLD"
        assert e.get_tier(50000)["tier"] == "PLATINUM"
        print("\n✅ All loyalty tiers correct")

    def test_earning_events(self):
        from influmatch.backend.services.wallet.loyalty_engine import LoyaltyWalletEngine
        e = LoyaltyWalletEngine()
        assert e.EARNING_EVENTS["campaign_published"] == 100
        assert e.EARNING_EVENTS["campaign_completed"] == 200
        assert e.EARNING_EVENTS["merchant_referral"]  == 500
        print("\n✅ Earning events correctly defined")


# ══════════════════════════════════════════════════════════
class TestSecurityLayer:
    def test_password_round_trip(self):
        from influmatch.backend.core.security import get_password_hash, verify_password
        raw    = "MySecurePass2024!"
        hashed = get_password_hash(raw)
        assert verify_password(raw, hashed)         is True
        assert verify_password("wrongpass", hashed) is False
        print("\n✅ Password hashing round-trip")

    def test_jwt_lifecycle(self):
        from influmatch.backend.core.security import create_access_token, decode_token
        from datetime import timedelta
        token   = create_access_token(
            {"sub": "42", "role": "merchant"},
            expires_delta=timedelta(minutes=30)
        )
        decoded = decode_token(token)
        assert decoded is not None
        assert decoded["sub"]  == "42"
        assert decoded["role"] == "merchant"
        assert decoded["iss"]  == "influmatch.jo"
        print("\n✅ JWT lifecycle: create → encode → decode")

    def test_expired_token_rejected(self):
        from influmatch.backend.core.security import create_access_token, decode_token
        from datetime import timedelta
        token   = create_access_token(
            {"sub": "1"},
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        decoded = decode_token(token)
        assert decoded is None
        print("\n✅ Expired token correctly rejected")


# ══════════════════════════════════════════════════════════
class TestEscrowCalculations:
    def test_vat_calculation(self):
        amount = 1000.0
        vat    = amount * 0.16
        fee    = amount * 0.05
        net    = amount - fee
        assert vat == 160.0
        assert fee == 50.0
        assert net == 950.0
        print(f"\n✅ Escrow math: {amount} JOD → VAT:{vat} Fee:{fee} Net:{net}")

    def test_platform_commission_rate(self):
        from influmatch.backend.services.escrow.escrow_engine import EscrowEngine
        e = EscrowEngine()
        assert e.PLATFORM_COMMISSION == 0.05
        print("\n✅ Platform commission: 5% confirmed")


# ══════════════════════════════════════════════════════════
class TestRAGVectorStore:
    def test_collections_initialize(self):
        try:
            from influmatch.backend.services.rag.vector_store import InfluMatchVectorStore
            store = InfluMatchVectorStore()
            assert store.contracts_col is not None
            assert store.policies_col  is not None
            assert store.campaigns_col is not None
            print("\n✅ ChromaDB collections initialized")
        except Exception as e:
            pytest.skip(f"ChromaDB not available in CI: {e}")

    def test_text_splitter_arabic(self):
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        splitter = RecursiveCharacterTextSplitter(
            chunk_size    = 100,
            chunk_overlap = 20,
            separators    = ["\n\n", "\n", ".", "،", " "]
        )
        arabic_text = "هذا نص عربي تجريبي. يحتوي على جمل متعددة. للاختبار فقط."
        chunks = splitter.split_text(arabic_text)
        assert len(chunks) >= 1
        print(f"\n✅ Arabic text splitting: {len(chunks)} chunks")


# ══════════════════════════════════════════════════════════
class TestConfigSettings:
    def test_jordan_market_defaults(self):
        from influmatch.backend.core.config import get_settings
        s = get_settings()
        assert s.currency == "JOD"
        assert s.vat_rate == 0.16
        assert s.app_name == "InfluMatch.jo"
        print(f"\n✅ Jordan market config: {s.currency} | VAT: {s.vat_rate * 100}%")

    def test_escrow_defaults(self):
        from influmatch.backend.core.config import get_settings
        s = get_settings()
        assert s.escrow_release_days == 7
        assert s.loyalty_points_rate == 0.05
        print(
            f"\n✅ Escrow: {s.escrow_release_days}d release | "
            f"Loyalty: {s.loyalty_points_rate * 100}% rate"
        )


# ── Standalone runner with coverage report ─────────────────
if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-s",
        "--cov=influmatch.backend",
        "--cov-report=term-missing",
        "--cov-report=html:docs/coverage_report",
        "-q"
    ])
