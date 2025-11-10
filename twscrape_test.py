# twscrape_test.py
import asyncio
from twscrape import API

async def main():
    api = API()
    pool = api.pool

    # Try to list sessions/accounts without calling load()/refresh()
    try:
        if hasattr(pool, "sessions"):
            print(f"Sessions: {len(pool.sessions)}")
            for s in pool.sessions:
                print(" -", getattr(s, "username", "?"))
        elif hasattr(pool, "accounts"):
            print(f"Accounts: {len(pool.accounts)}")
            for a in pool.accounts:
                print(" -", getattr(a, "username", "?"))
        else:
            print("⚠️ Pool does not expose sessions/accounts attributes in this build.")
    except Exception as e:
        print("⚠️ Could not inspect pool:", e)

    # Try an actual search (works even if the pool didn’t list sessions)
    try:
        q = "Apple lang:en"
        print(f"\nSearching: {q}\n")
        got = 0
        async for tw in api.search(q, limit=5):
            txt = getattr(tw, "rawContent", None) or getattr(tw, "text", "")
            print("-", (txt or "").strip()[:120])
            got += 1
        if got:
            print(f"\n✅ twscrape fetched {got} tweets")
        else:
            print("\n❌ No tweets returned (session/cookies may not be active).")
    except Exception as e:
        print("\n❌ Search error:", repr(e))

if __name__ == "__main__":
    asyncio.run(main())
