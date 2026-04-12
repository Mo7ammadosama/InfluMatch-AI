#!/usr/bin/env python3
"""Database initialization — creates tables + admin user"""
import asyncio, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent / "influmatch"
sys.path.insert(0, str(ROOT))

async def init():
    from backend.core.database import init_db, AsyncSessionLocal
    from backend.core.security import get_password_hash
    from backend.models.user import User, UserRole

    await init_db()
    print("[DB] Tables created")

    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.username == "godmode_admin"))
        if not result.scalar_one_or_none():
            admin = User(
                email="admin@influmatch.jo",
                username="godmode_admin",
                hashed_password=get_password_hash("aria_admin_2024"),
                role=UserRole.ADMIN,
                full_name_en="ARIA God Mode Admin",
                full_name_ar="مشرف النظام",
                is_active=True,
                is_verified=True
            )
            db.add(admin)
            await db.commit()
            print("[DB] Admin user created: admin@influmatch.jo / aria_admin_2024")
        else:
            print("[DB] Admin user already exists")

    print("[DB] Database initialization complete")

if __name__ == "__main__":
    asyncio.run(init())
