"""
WaslAI.jo — Realistic seed data for QA/testing.
Uses actual DB column names verified by PRAGMA table_info.
"""
import asyncio, json, uuid
from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

DB_PATH = Path("influmatch/influmatch.db")
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"


async def main():
    engine = create_async_engine(DATABASE_URL, echo=False)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as db:
        # ── 0. Fetch user IDs ──────────────────────────────────────────────────
        rows = (await db.execute(text("SELECT id, email, role FROM users"))).fetchall()
        users = {r.email: {"id": r.id, "role": r.role} for r in rows}
        print("Users found:", [e for e in users if "@waslai.jo" in e])

        merchant_uid   = users.get("merchant@waslai.jo",   {}).get("id")
        influencer_uid = users.get("influencer@waslai.jo", {}).get("id")
        creator_uid    = users.get("creator@waslai.jo",    {}).get("id")
        strategist_uid = users.get("strategist@waslai.jo", {}).get("id")

        if not merchant_uid:
            print("ERROR: merchant@waslai.jo not found — run setup_accounts.py first")
            return

        # ── 1. Merchant profile ────────────────────────────────────────────────
        exists = (await db.execute(
            text("SELECT id FROM merchants WHERE user_id = :uid"), {"uid": merchant_uid}
        )).fetchone()
        if not exists:
            mid = str(uuid.uuid4())
            await db.execute(text("""
                INSERT INTO merchants (id, user_id, business_name, business_category, city,
                    description, website, active_campaigns, is_verified, created_at, updated_at)
                VALUES (:id, :uid, 'TechJo Solutions', 'technology', 'Amman',
                    'Leading tech company in Jordan', 'https://techjo.jo', 0, 1, :now, :now)
            """), {"id": mid, "uid": merchant_uid, "now": datetime.utcnow()})
            print(f"Created merchant profile: {mid}")
        else:
            mid = exists.id
            print(f"Merchant profile exists: {mid}")
        merchant_id = mid

        # ── 2. Influencer profile ──────────────────────────────────────────────
        exists = (await db.execute(
            text("SELECT id FROM influencers WHERE user_id = :uid"), {"uid": influencer_uid}
        )).fetchone() if influencer_uid else None
        if influencer_uid and not exists:
            iid = str(uuid.uuid4())
            await db.execute(text("""
                INSERT INTO influencers (id, user_id, display_name, bio, city,
                    social_platforms, content_categories, languages, total_followers,
                    avg_engagement_rate, rate_per_post_jod, rate_per_story_jod, rate_per_reel_jod,
                    is_available, is_verified, avg_rating, total_earned_jod, completed_deals,
                    created_at, updated_at)
                VALUES (:id, :uid, 'Sarah Al-Ahmad',
                    'Fashion & lifestyle influencer based in Amman. Bilingual AR/EN.',
                    'Amman', :social, :cats, '["ar","en"]', 67000, 4.2, 150.0, 80.0, 120.0,
                    1, 1, 4.8, 0.0, 0, :now, :now)
            """), {
                "id": iid, "uid": influencer_uid,
                "social": json.dumps({"instagram": {"followers": 45000, "handle": "@sarahjordan"},
                                      "tiktok": {"followers": 22000, "handle": "@sarahjordan"}}),
                "cats": json.dumps(["fashion", "lifestyle", "beauty"]),
                "now": datetime.utcnow(),
            })
            print(f"Created influencer profile: {iid}")
            influencer_id = iid
        elif influencer_uid and exists:
            influencer_id = exists.id
            print(f"Influencer profile exists: {influencer_id}")
        else:
            influencer_id = None

        # ── 3. Influencer profile for strategist (INFLUENCER role) ─────────────
        exists = (await db.execute(
            text("SELECT id FROM influencers WHERE user_id = :uid"), {"uid": strategist_uid}
        )).fetchone() if strategist_uid else None
        if strategist_uid and not exists:
            sid = str(uuid.uuid4())
            await db.execute(text("""
                INSERT INTO influencers (id, user_id, display_name, bio, city,
                    social_platforms, content_categories, languages, total_followers,
                    avg_engagement_rate, rate_per_post_jod, rate_per_story_jod, rate_per_reel_jod,
                    is_available, is_verified, avg_rating, total_earned_jod, completed_deals,
                    created_at, updated_at)
                VALUES (:id, :uid, 'Omar Al-Khalidi',
                    'Creative Strategist & campaign ideator. 5+ years in digital marketing.',
                    'Amman', :social, :cats, '["ar","en"]', 12000, 6.1, 200.0, 100.0, 160.0,
                    1, 1, 4.9, 0.0, 0, :now, :now)
            """), {
                "id": sid, "uid": strategist_uid,
                "social": json.dumps({"instagram": {"followers": 12000, "handle": "@creativejordan"}}),
                "cats": json.dumps(["marketing", "strategy", "digital"]),
                "now": datetime.utcnow(),
            })
            print(f"Created strategist influencer profile: {sid}")
            strategist_inf_id = sid
        elif strategist_uid and exists:
            strategist_inf_id = exists.id
            print(f"Strategist influencer profile exists: {strategist_inf_id}")
        else:
            strategist_inf_id = None

        # ── 4. Content Creator profile ─────────────────────────────────────────
        exists = (await db.execute(
            text("SELECT id FROM content_creators WHERE user_id = :uid"), {"uid": creator_uid}
        )).fetchone() if creator_uid else None
        if creator_uid and not exists:
            ccid = str(uuid.uuid4())
            await db.execute(text("""
                INSERT INTO content_creators (id, user_id, display_name, bio, city,
                    specializations, languages, content_categories, consultation_rate_jod,
                    is_available, is_verified, avg_rating, total_earned_jod,
                    completed_engagements, created_at, updated_at)
                VALUES (:id, :uid, 'Lina Bakri',
                    'Professional content creator specializing in video & photography for brands.',
                    'Amman', :specs, '["ar","en"]', :cats, 300.0, 1, 1, 4.8, 0.0, 0, :now, :now)
            """), {
                "id": ccid, "uid": creator_uid,
                "specs": json.dumps(["video_production", "photography", "copywriting"]),
                "cats": json.dumps(["food", "travel", "technology"]),
                "now": datetime.utcnow(),
            })
            print(f"Created content creator profile: {ccid}")
            creator_id = ccid
        elif creator_uid and exists:
            creator_id = exists.id
            print(f"Content creator profile exists: {creator_id}")
        else:
            creator_id = None

        # ── 5. Campaigns ───────────────────────────────────────────────────────
        existing_camps = (await db.execute(
            text("SELECT id FROM campaigns WHERE merchant_id = :mid LIMIT 1"), {"mid": merchant_id}
        )).fetchone()
        if not existing_camps:
            camp_ids = []
            campaigns = [
                {
                    "id": str(uuid.uuid4()),
                    "title": "Ramadan Campaign 2026",
                    "title_ar": "حملة رمضان 2026",
                    "description": "Promote our Ramadan special products across Jordan via authentic content",
                    "description_ar": "روّج لمنتجاتنا الخاصة برمضان في الأردن",
                    "target_categories": json.dumps(["lifestyle", "food"]),
                    "required_platforms": json.dumps(["instagram", "tiktok"]),
                    "min_followers": 10000,
                    "min_engagement_rate": 3.0,
                    "preferred_languages": json.dumps(["ar", "en"]),
                    "target_cities": json.dumps(["Amman", "Irbid", "Zarqa"]),
                    "deliverables": json.dumps(["3 Instagram posts", "2 TikTok videos", "5 stories"]),
                    "total_budget_jod": 2000.0,
                    "max_influencers": 5,
                    "status": "active",
                    "start_date": (datetime.utcnow() + timedelta(days=5)).date().isoformat(),
                    "end_date": (datetime.utcnow() + timedelta(days=35)).date().isoformat(),
                    "ai_brief_summary": "Ramadan campaign focusing on family moments and traditional products",
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Tech Product Launch",
                    "title_ar": "إطلاق منتج تقني",
                    "description": "Launch our new SaaS product to Jordanian SMEs with bilingual influencers",
                    "description_ar": "أطلق منتجنا الجديد للشركات الصغيرة الأردنية",
                    "target_categories": json.dumps(["technology", "business"]),
                    "required_platforms": json.dumps(["linkedin", "instagram"]),
                    "min_followers": 5000,
                    "min_engagement_rate": 2.5,
                    "preferred_languages": json.dumps(["ar", "en"]),
                    "target_cities": json.dumps(["Amman"]),
                    "deliverables": json.dumps(["2 LinkedIn articles", "3 Instagram reels", "product demo"]),
                    "total_budget_jod": 3500.0,
                    "max_influencers": 3,
                    "status": "active",
                    "start_date": (datetime.utcnow() + timedelta(days=10)).date().isoformat(),
                    "end_date": (datetime.utcnow() + timedelta(days=40)).date().isoformat(),
                    "ai_brief_summary": "B2B SaaS launch targeting Jordanian entrepreneurs",
                },
            ]
            for camp in campaigns:
                await db.execute(text("""
                    INSERT INTO campaigns (id, merchant_id, title, title_ar, description, description_ar,
                        target_categories, required_platforms, min_followers, min_engagement_rate,
                        preferred_languages, target_cities, deliverables, total_budget_jod, spent_budget_jod,
                        max_influencers, start_date, end_date, status, ai_brief_summary, created_at, updated_at)
                    VALUES (:id, :merchant_id, :title, :title_ar, :description, :description_ar,
                        :target_categories, :required_platforms, :min_followers, :min_engagement_rate,
                        :preferred_languages, :target_cities, :deliverables, :total_budget_jod, 0.0,
                        :max_influencers, :start_date, :end_date, :status, :ai_brief_summary, :now, :now)
                """), {**camp, "merchant_id": merchant_id, "now": datetime.utcnow()})
                camp_ids.append(camp["id"])
            await db.execute(text("UPDATE merchants SET active_campaigns = :n WHERE id = :mid"),
                {"n": len(campaigns), "mid": merchant_id})
            print(f"Created {len(campaigns)} campaigns")
        else:
            rows2 = (await db.execute(
                text("SELECT id FROM campaigns WHERE merchant_id = :mid"), {"mid": merchant_id}
            )).fetchall()
            camp_ids = [r.id for r in rows2]
            print(f"Campaigns exist: {len(camp_ids)}")
        campaign_id = camp_ids[0] if camp_ids else None

        # ── 6. Deal + Escrow ───────────────────────────────────────────────────
        if influencer_id and campaign_id:
            existing_deal = (await db.execute(
                text("SELECT id FROM deals WHERE campaign_id = :cid LIMIT 1"), {"cid": campaign_id}
            )).fetchone()
            if not existing_deal:
                escrow_id = str(uuid.uuid4())
                deal_id   = str(uuid.uuid4())
                gross = 500.0
                fee   = round(gross * 0.10, 3)
                vat   = round(fee * 0.16, 3)
                net   = round(gross - fee - vat, 3)
                await db.execute(text("""
                    INSERT INTO escrow_transactions (id, merchant_id, influencer_id, gross_amount_jod,
                        platform_fee_jod, vat_on_fee_jod, net_to_influencer_jod, state, created_at, updated_at)
                    VALUES (:id, :mid, :iid, :gross, :fee, :vat, :net, 'funded', :now, :now)
                """), {"id": escrow_id, "mid": merchant_id, "iid": influencer_id,
                       "gross": gross, "fee": fee, "vat": vat, "net": net, "now": datetime.utcnow()})

                await db.execute(text("""
                    INSERT INTO deals (id, campaign_id, influencer_id, agreed_amount_jod,
                        vat_amount_jod, platform_fee_jod, total_amount_jod, deliverables,
                        deadline, notes, escrow_id, status, content_urls, content_verified_by_ai,
                        created_at, updated_at)
                    VALUES (:id, :cid, :iid, :amt, :vat, :fee, :total, :deliv,
                        :deadline, 'Seeded for QA testing', :eid, 'proposed', '[]', 0, :now, :now)
                """), {
                    "id": deal_id, "cid": campaign_id, "iid": influencer_id,
                    "amt": gross, "vat": vat, "fee": fee, "total": round(gross + vat + fee, 3),
                    "deliv": json.dumps(["3 Instagram posts", "2 TikTok videos"]),
                    "deadline": (datetime.utcnow() + timedelta(days=21)).isoformat(),
                    "eid": escrow_id, "now": datetime.utcnow(),
                })
                print(f"Created deal {deal_id} with escrow {escrow_id}")
            else:
                deal_id = existing_deal.id
                print(f"Deal exists: {deal_id}")
        else:
            deal_id = None

        # ── 7. Messages ────────────────────────────────────────────────────────
        if deal_id and merchant_uid:
            existing_msg = (await db.execute(
                text("SELECT id FROM messages WHERE deal_id = :did LIMIT 1"), {"did": deal_id}
            )).fetchone()
            if not existing_msg:
                for content in [
                    "مرحباً! أنا متحمس للعمل على هذه الحملة.",
                    "Hello! Looking forward to hearing your content ideas.",
                    "What platforms will you primarily use for this campaign?",
                ]:
                    await db.execute(text("""
                        INSERT INTO messages (id, deal_id, sender_id, content, created_at)
                        VALUES (:id, :did, :sid, :content, :now)
                    """), {"id": str(uuid.uuid4()), "did": deal_id,
                          "sid": merchant_uid, "content": content, "now": datetime.utcnow()})
                print("Created messages")
            else:
                print("Messages exist")

        # ── 8. Campaign Idea from strategist ──────────────────────────────────
        if strategist_uid:
            existing_idea = (await db.execute(
                text("SELECT id FROM campaign_ideas WHERE user_id = :uid LIMIT 1"), {"uid": strategist_uid}
            )).fetchone()
            if not existing_idea:
                idea_id = str(uuid.uuid4())
                await db.execute(text("""
                    INSERT INTO campaign_ideas (id, user_id, title, title_ar, description, description_ar,
                        target_audience, suggested_platforms, content_format, influencer_type,
                        business_category, estimated_budget_jod, timeline_days, status,
                        view_count, adoption_count, created_at, updated_at)
                    VALUES (:id, :uid,
                        'Ramadan UGC Series for F&B Brands',
                        'سلسلة محتوى رمضان للمطاعم والأغذية',
                        'Authentic family moments and traditional recipes during Ramadan. Targeting F&B brands wanting emotional connection.',
                        'لحظات عائلية أصيلة ووصفات تقليدية خلال رمضان. للعلامات الغذائية التي تريد تواصلاً عاطفياً.',
                        'Jordanian families aged 25-50, Arabic speaking',
                        :platforms, :formats, 'family_nano', 'food_beverage',
                        1500.0, 30, 'open', 3, 0, :now, :now)
                """), {
                    "id": idea_id, "uid": strategist_uid,
                    "platforms": json.dumps(["instagram", "tiktok"]),
                    "formats": json.dumps(["video", "stories", "reels"]),
                    "now": datetime.utcnow(),
                })
                print(f"Created campaign idea: {idea_id}")
            else:
                print(f"Campaign idea exists: {existing_idea.id}")

        # ── 9. Wallet for influencer ───────────────────────────────────────────
        for uid, label, balance in [
            (influencer_uid, "influencer", 250.5),
            (merchant_uid, "merchant", 5000.0),
        ]:
            if uid:
                existing = (await db.execute(
                    text("SELECT id FROM wallets WHERE user_id = :uid"), {"uid": uid}
                )).fetchone()
                if not existing:
                    wid = str(uuid.uuid4())
                    await db.execute(text("""
                        INSERT INTO wallets (id, user_id, available_balance_jod, locked_balance_jod,
                            points_balance, total_points_earned, points_to_jod_rate, created_at, updated_at)
                        VALUES (:id, :uid, :bal, 0.0, 500, 1200, 0.01, :now, :now)
                    """), {"id": wid, "uid": uid, "bal": balance, "now": datetime.utcnow()})
                    await db.execute(text("""
                        INSERT INTO wallet_transactions (id, wallet_id, transaction_type, amount_jod,
                            points_delta, balance_after_jod, description, created_at)
                        VALUES (:id, :wid, 'credit', :bal, 500, :bal,
                            'Initial seed credit for QA testing', :now)
                    """), {"id": str(uuid.uuid4()), "wid": wid, "bal": balance, "now": datetime.utcnow()})
                    print(f"Created wallet for {label}: {wid}")
                else:
                    print(f"{label.title()} wallet exists: {existing.id}")

        await db.commit()
        print("\nSeed data committed successfully.")

        # Print summary for test scripts
        print("\n=== SEED DATA SUMMARY ===")
        print(f"Merchant ID   : {merchant_id}")
        print(f"Influencer ID : {influencer_id}")
        print(f"Creator ID    : {creator_id}")
        print(f"Campaign ID   : {campaign_id}")
        print(f"Deal ID       : {deal_id}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
