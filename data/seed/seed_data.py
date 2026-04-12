"""
InfluMatch.jo — Database Seed Script
Populates dev database with realistic Jordan market data
Run: python data/seed/seed_data.py
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import AsyncSessionLocal, create_tables
from app.models.user import User, UserRole
from app.models.merchant import Merchant
from app.models.influencer import Influencer
from app.models.wallet import Wallet
from app.services.auth_service import hash_password


SEED_MERCHANTS = [
    {
        "user": {"email": "zara.jo@test.com", "full_name": "Zara Jordan", "full_name_ar": "زارا الأردن", "role": UserRole.MERCHANT, "phone": "+96279111001"},
        "merchant": {"business_name": "Zara Jordan", "business_name_ar": "زارا الأردن", "business_category": "fashion", "city": "Amman", "is_verified": True},
    },
    {
        "user": {"email": "tastejo@test.com", "full_name": "Taste Jo Restaurant", "full_name_ar": "مطعم تيست جو", "role": UserRole.MERCHANT, "phone": "+96279111002"},
        "merchant": {"business_name": "Taste Jo", "business_name_ar": "تيست جو", "business_category": "food", "city": "Amman"},
    },
    {
        "user": {"email": "techhubjordan@test.com", "full_name": "Tech Hub Jordan", "full_name_ar": "تك هب الأردن", "role": UserRole.MERCHANT, "phone": "+96279111003"},
        "merchant": {"business_name": "Tech Hub Jordan", "business_name_ar": "تك هب الأردن", "business_category": "tech", "city": "Amman", "website": "https://techhub.jo"},
    },
]

SEED_INFLUENCERS = [
    {
        "user": {"email": "sara.influencer@test.com", "full_name": "Sara Al-Khatib", "full_name_ar": "سارة الخطيب", "role": UserRole.INFLUENCER, "phone": "+96279222001"},
        "influencer": {
            "display_name": "Sara Fashion", "bio": "Fashion & lifestyle blogger from Amman",
            "bio_ar": "مدونة أزياء وأسلوب حياة من عمان", "city": "Amman",
            "social_platforms": {"instagram": {"handle": "@sarafashion", "followers": 85000, "engagement_rate": 0.045}},
            "total_followers": 85000, "avg_engagement_rate": 0.045,
            "content_categories": ["fashion", "lifestyle", "beauty"],
            "languages": ["ar", "en"], "rate_per_post_jod": 150.0, "rate_per_story_jod": 75.0,
            "rate_per_reel_jod": 200.0, "is_verified": True,
        },
    },
    {
        "user": {"email": "ahmad.food@test.com", "full_name": "Ahmad Al-Masri", "full_name_ar": "أحمد المصري", "role": UserRole.INFLUENCER, "phone": "+96279222002"},
        "influencer": {
            "display_name": "Ahmad Eats", "bio": "Food & travel content creator | Jordan",
            "bio_ar": "صانع محتوى طعام وسفر | الأردن", "city": "Amman",
            "social_platforms": {
                "instagram": {"handle": "@ahmadeats", "followers": 42000, "engagement_rate": 0.062},
                "tiktok": {"handle": "@ahmadeats", "followers": 98000, "engagement_rate": 0.08},
            },
            "total_followers": 140000, "avg_engagement_rate": 0.071,
            "content_categories": ["food", "travel", "lifestyle"],
            "languages": ["ar"], "rate_per_post_jod": 80.0, "rate_per_story_jod": 40.0,
            "rate_per_reel_jod": 120.0,
        },
    },
    {
        "user": {"email": "lina.tech@test.com", "full_name": "Lina Haddad", "full_name_ar": "لينا حداد", "role": UserRole.INFLUENCER, "phone": "+96279222003"},
        "influencer": {
            "display_name": "Lina Tech", "bio": "Tech reviewer & gadget enthusiast in Jordan",
            "bio_ar": "مراجعة تقنية وعشق التكنولوجيا في الأردن", "city": "Amman",
            "social_platforms": {"youtube": {"handle": "LinaTechJO", "followers": 55000, "engagement_rate": 0.038}},
            "total_followers": 55000, "avg_engagement_rate": 0.038,
            "content_categories": ["tech", "lifestyle"],
            "languages": ["ar", "en"], "rate_per_post_jod": 100.0, "rate_per_story_jod": 50.0,
            "rate_per_reel_jod": 175.0, "is_verified": True,
        },
    },
]

DEFAULT_PASSWORD = "InfluMatch@2024"


async def seed():
    print("🌱 Seeding InfluMatch.jo database...")
    await create_tables()

    async with AsyncSessionLocal() as db:
        for m_data in SEED_MERCHANTS:
            u_data = m_data["user"]
            user = User(hashed_password=hash_password(DEFAULT_PASSWORD), is_verified=True, **u_data)
            db.add(user)
            await db.flush()
            merchant = Merchant(user_id=user.id, **m_data["merchant"])
            db.add(merchant)
            wallet = Wallet(user_id=user.id)
            db.add(wallet)
            print(f"  ✅ Merchant: {u_data['full_name']}")

        for i_data in SEED_INFLUENCERS:
            u_data = i_data["user"]
            user = User(hashed_password=hash_password(DEFAULT_PASSWORD), is_verified=True, **u_data)
            db.add(user)
            await db.flush()
            influencer = Influencer(user_id=user.id, **i_data["influencer"])
            db.add(influencer)
            wallet = Wallet(user_id=user.id)
            db.add(wallet)
            print(f"  ✅ Influencer: {u_data['full_name']}")

        await db.commit()
        print(f"\n🎉 Seeded {len(SEED_MERCHANTS)} merchants + {len(SEED_INFLUENCERS)} influencers")
        print(f"   Default password: {DEFAULT_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(seed())
