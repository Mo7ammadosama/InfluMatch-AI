"""
Create/reset test users for Playwright E2E tests.
Run: python setup_test_users.py
"""
import sqlite3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.auth_service import hash_password

DB_PATH = "./influmatch/influmatch.db"
NEW_PASSWORD = "WaslAI@2026"

TEST_USERS = [
    {"email": "merchant@waslai.jo",   "full_name": "Test Merchant",   "role": "merchant"},
    {"email": "influencer@waslai.jo", "full_name": "Test Influencer", "role": "influencer"},
    {"email": "admin@waslai.jo",      "full_name": "Test Admin",      "role": "admin"},
]

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Show existing users
cur.execute("SELECT email, role, is_active, is_verified FROM users")
rows = cur.fetchall()
print("=== Existing users ===")
for r in rows:
    print(f"  {r[0]} | role={r[1]} | active={r[2]} | verified={r[3]}")
print()

hashed = hash_password(NEW_PASSWORD)

for u in TEST_USERS:
    email = u["email"]
    cur.execute("SELECT id, email FROM users WHERE email = ?", (email,))
    existing = cur.fetchone()
    if existing:
        # Update password and ensure active/verified
        cur.execute(
            "UPDATE users SET hashed_password=?, is_active=1, is_verified=1 WHERE email=?",
            (hashed, email)
        )
        print(f"  ✅ Updated password for {email}")
    else:
        import uuid
        uid = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO users (id, email, hashed_password, full_name, role, is_active, is_verified) VALUES (?,?,?,?,?,1,1)",
            (uid, email, hashed, u["full_name"], u["role"])
        )
        print(f"  ✅ Created user {email} ({u['role']})")

conn.commit()

# Also create wallets for new users
cur.execute("SELECT id, email FROM users WHERE email IN ('merchant@waslai.jo','influencer@waslai.jo','admin@waslai.jo')")
users = cur.fetchall()
for user_id, email in users:
    cur.execute("SELECT id FROM wallets WHERE user_id=?", (user_id,))
    wallet = cur.fetchone()
    if not wallet:
        w_id = str(uuid.uuid4())
        cur.execute(
            "INSERT INTO wallets (id, user_id) VALUES (?,?)",
            (w_id, user_id)
        )
        print(f"  💳 Created wallet for {email}")

conn.commit()

print()
print("=== Final test users ===")
cur.execute("SELECT email, role, is_active, is_verified FROM users WHERE email LIKE '%waslai.jo'")
for r in cur.fetchall():
    print(f"  {r[0]} | role={r[1]} | active={r[2]} | verified={r[3]}")

conn.close()
print(f"\nAll test users set with password: {NEW_PASSWORD}")
