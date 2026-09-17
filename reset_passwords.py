import sqlite3, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.services.auth_service import hash_password

DB_PATH = "./influmatch/influmatch.db"
NEW_PASSWORD = "WaslAI@2026"
EMAILS = ["merchant@waslai.jo", "influencer@waslai.jo", "admin@waslai.jo"]

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
hashed = hash_password(NEW_PASSWORD)

for email in EMAILS:
    cur.execute(
        "UPDATE users SET hashed_password=?, is_active=1, is_verified=1 WHERE email=?",
        (hashed, email)
    )
    print("Updated: " + email + " rows=" + str(cur.rowcount))

conn.commit()
print("Done. Password set to: " + NEW_PASSWORD)
conn.close()
