"""Fix all lowercase enum values in DB to uppercase names (SQLAlchemy default for non-native enums)."""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def main():
    engine = create_async_engine("sqlite+aiosqlite:///influmatch/influmatch.db")
    async with engine.begin() as conn:
        tables = [
            ("campaign_ideas", "status"),
            ("escrow_transactions", "state"),
            ("deals", "status"),
            ("creative_engagements", "status"),
            ("wallet_transactions", "transaction_type"),
            ("booking_requests", "status"),
            ("campaigns", "status"),
            ("cc_engagements", "status"),
        ]
        for table, col in tables:
            try:
                sql = f"UPDATE {table} SET {col} = UPPER({col}) WHERE {col} != UPPER({col})"
                r = await conn.execute(text(sql))
                if r.rowcount > 0:
                    print(f"Fixed {table}.{col}: {r.rowcount} rows updated")
                else:
                    print(f"  {table}.{col}: already correct")
            except Exception as e:
                print(f"  {table}: skip ({e})")

    async with engine.connect() as conn:
        print("\nVerification:")
        for table, col in [("campaign_ideas", "status"), ("escrow_transactions", "state"),
                           ("deals", "status"), ("wallet_transactions", "transaction_type")]:
            try:
                rows = (await conn.execute(text(f"SELECT {col} FROM {table} LIMIT 5"))).fetchall()
                print(f"  {table}.{col}: {[r[0] for r in rows]}")
            except Exception as e:
                print(f"  {table}: {e}")

    await engine.dispose()
    print("\nDone — all enum values fixed to uppercase names.")

if __name__ == "__main__":
    asyncio.run(main())
