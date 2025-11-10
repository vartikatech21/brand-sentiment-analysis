# add_twscrape_session.py
# add_twscrape_session.py
import asyncio, json
from twscrape import API

def to_cookie_header(cookies_obj):
    # Cookie-Editor JSON (list of {name,value,...}) -> "name=value; name2=val2"
    if isinstance(cookies_obj, list):
        return "; ".join(f"{c['name']}={c['value']}" for c in cookies_obj if "name" in c and "value" in c)
    raise ValueError("cookies.json must be a list (Cookie-Editor export)")

async def main():
    api = API()
    pool = api.pool

    # 1) Try to purge an existing placeholder account
    try:
        if hasattr(pool, "accounts"):
            for acc in list(pool.accounts):
                if getattr(acc, "username", "") == "cookie_user":
                    if hasattr(pool, "remove_account"):
                        await pool.remove_account(acc)
                        print("🧹 removed old 'cookie_user'")
    except Exception as e:
        print("⚠️ couldn't purge old account:", e)

    # 2) Read cookies.json
    with open("cookies.json", "r", encoding="utf-8") as f:
        cookies = json.load(f)
    cookie_header = to_cookie_header(cookies)

    # 3) Try older API: import_session
    if hasattr(pool, "import_session"):
        try:
            await pool.import_session("cookies.json")
            if hasattr(pool, "accounts") and pool.accounts:
                acc = pool.accounts[-1]
                acc.username = "cookie_user"
                if hasattr(pool, "save"):
                    await pool.save(acc)
            print("✅ twscrape session saved via import_session()")
            return
        except Exception as e:
            print("ℹ️ import_session failed, trying add_account(cookies=...):", e)

    # 4) Fallback: add_account with cookies header
    try:
        acc = await pool.add_account(
            username="cookie_user",
            password="x",
            email="cookie@example.com",
            email_password="x",
            cookies=cookie_header,
        )

        # persist if a save-like method exists
        saved = False
        for method in ("save", "commit", "flush"):
            if hasattr(pool, method):
                try:
                    await getattr(pool, method)(acc)
                    print(f"✅ twscrape session saved via add_account() using {method}()")
                    saved = True
                    break
                except Exception:
                    pass
        if not saved:
            print("✅ twscrape account added (no explicit save method found; some builds persist automatically)")

    except Exception as e:
        print("❌ Could not add account with cookies:", e)
        raise

if __name__ == "__main__":
    asyncio.run(main())


