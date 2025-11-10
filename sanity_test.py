# sanity_test.py
import os, itertools, time
from backend.twitter_cookies import ensure_cookies

# load & print which cookie file is used
ensure_cookies()
print("COOKIES:", os.getenv("SNSCRAPE_TWITTER_COOKIES_FILE") or "None")

import snscrape.modules.twitter as snt

query = "Apple lang:en"   # english-only helps stability

def try_scrape(q, n=5):
    it = snt.TwitterSearchScraper(q).get_items()
    for t in itertools.islice(it, n):
        print(t.date, "-", t.user.username, "-", t.rawContent[:80])
    print("✅ snscrape working")

try:
    try_scrape(query)
except Exception as e:
    print("❌ First attempt failed:", repr(e))
    # tiny backoff + one retry
    time.sleep(3)
    try:
        try_scrape(query)
    except Exception as e2:
        print("❌ Retry failed:", repr(e2))
        print("Hint: cookies may be expired OR Twitter is rate-limiting (429).")

