import sqlite3
import sys
sys.path.insert(0, ".")

for db in ["waslai.db", "influmatch.db"]:
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        print(f"{db}: {tables}")
        if "users" in tables:
            cur.execute("SELECT email, role, is_active, is_verified FROM users LIMIT 20")
            for r in cur.fetchall():
                print(f"  {r}")
        conn.close()
    except Exception as e:
        print(f"{db}: ERROR - {e}")
