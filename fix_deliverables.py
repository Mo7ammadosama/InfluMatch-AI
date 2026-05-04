"""Fix deliverables JSON arrays -> dicts in deals table."""
import asyncio, json
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def main():
    engine = create_async_engine("sqlite+aiosqlite:///influmatch/influmatch.db")
    async with engine.begin() as conn:
        rows = (await conn.execute(text("SELECT id, deliverables FROM deals"))).fetchall()
        for row in rows:
            raw = row[1]
            try:
                d = json.loads(raw) if raw else {}
            except Exception:
                d = {}
            if isinstance(d, list):
                fixed = json.dumps({item: True for item in d})
                await conn.execute(
                    text("UPDATE deals SET deliverables=:v WHERE id=:id"),
                    {"v": fixed, "id": row[0]}
                )
                print(f"Fixed deal {row[0]}: list -> dict")
            else:
                print(f"  deal {row[0]}: already dict")
    await engine.dispose()
    print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
