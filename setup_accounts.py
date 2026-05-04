import sqlite3, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.services.auth_service import hash_password
from datetime import datetime

DB = "./influmatch/influmatch.db"
PASSWORD = "WaslAI@2026"

USERS = [
    ("merchant@waslai.jo",          "merchant_waslai",    "MERCHANT",         "WaslAI Merchant",   "تاجر واصل"),
    ("influencer@waslai.jo",        "influencer_waslai",  "INFLUENCER",       "WaslAI Influencer", "مؤثر واصل"),
    ("admin@waslai.jo",             "admin_waslai",       "ADMIN",            "WaslAI Admin",      "مدير واصل"),
    ("creator@waslai.jo",           "creator_waslai",     "CONTENT_CREATOR",  "WaslAI Creator",    "منشئ واصل"),
    ("strategist@waslai.jo",        "strategist_waslai",  "INFLUENCER",       "WaslAI Strategist", "استراتيجي واصل"),
]

conn = sqlite3.connect(DB)
cur = conn.cursor()

# Check schema
cur.execute("PRAGMA table_info(users)")
cols = [row[1] for row in cur.fetchall()]
print("Users columns:", cols)

hashed = hash_password(PASSWORD)
now = datetime.utcnow().isoformat()

for email, username, role, name_en, name_ar in USERS:
    cur.execute("SELECT id FROM users WHERE email=?", (email,))
    if cur.fetchone():
        # Build update dynamically based on available columns
        update_parts = ["hashed_password=?", "is_active=1", "is_verified=1"]
        params = [hashed]
        if "role" in cols:
            update_parts.append("role=?"); params.append(role)
        if "full_name_en" in cols:
            update_parts.append("full_name_en=?"); params.append(name_en)
        elif "full_name" in cols:
            update_parts.append("full_name=?"); params.append(name_en)
        if "full_name_ar" in cols:
            update_parts.append("full_name_ar=?"); params.append(name_ar)
        if "updated_at" in cols:
            update_parts.append("updated_at=?"); params.append(now)
        params.append(email)
        cur.execute(f"UPDATE users SET {', '.join(update_parts)} WHERE email=?", params)
        print(f"Updated : {email}")
    else:
        # Insert with available columns
        import uuid as _uuid
        insert_cols = ["id", "email", "hashed_password", "is_active", "is_verified"]
        insert_vals = [str(_uuid.uuid4()), email, hashed, 1, 1]
        if "username" in cols:
            insert_cols.append("username"); insert_vals.append(username)
        if "role" in cols:
            insert_cols.append("role"); insert_vals.append(role)
        if "full_name_en" in cols:
            insert_cols.append("full_name_en"); insert_vals.append(name_en)
        elif "full_name" in cols:
            insert_cols.append("full_name"); insert_vals.append(name_en)
        if "full_name_ar" in cols:
            insert_cols.append("full_name_ar"); insert_vals.append(name_ar)
        if "created_at" in cols:
            insert_cols.append("created_at"); insert_vals.append(now)
        if "updated_at" in cols:
            insert_cols.append("updated_at"); insert_vals.append(now)
        placeholders = ",".join("?" * len(insert_vals))
        cur.execute(f"INSERT INTO users ({','.join(insert_cols)}) VALUES ({placeholders})", insert_vals)
        print(f"Created : {email}")

conn.commit()

# Also ensure wallets exist
try:
    cur.execute("SELECT id, email FROM users WHERE email IN ('merchant@waslai.jo','influencer@waslai.jo','admin@waslai.jo','creator@waslai.jo','strategist@waslai.jo')")
    users = cur.fetchall()
    for user_id, email in users:
        cur.execute("SELECT id FROM wallets WHERE user_id=?", (user_id,))
        if not cur.fetchone():
            import uuid
            cur.execute("INSERT INTO wallets (id, user_id) VALUES (?,?)", (str(uuid.uuid4()), user_id))
            print(f"Created wallet for {email}")
    conn.commit()
except Exception as e:
    print(f"Wallet step skipped: {e}")

conn.close()

# Verify
conn2 = sqlite3.connect(DB)
cur2 = conn2.cursor()
cur2.execute("SELECT email, role, is_active, is_verified FROM users WHERE email LIKE '%waslai.jo'")
print("\n=== Final test accounts ===")
for r in cur2.fetchall():
    print(f"  {r[0]} | role={r[1]} | active={r[2]} | verified={r[3]}")
conn2.close()
print(f"\nAll accounts ready. Password = {PASSWORD}")
