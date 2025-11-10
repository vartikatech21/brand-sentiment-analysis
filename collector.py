# backend/collector.py
# backend/collector.py
from __future__ import annotations
from typing import List
from pathlib import Path
import os, json, time, hashlib, asyncio

import snscrape.modules.twitter as sntwitter
import snscrape.modules.reddit as snreddit

from .twitter_cookies import ensure_cookies
ensure_cookies()  # sets SNSCRAPE_TWITTER_COOKIES_FILE if a cookies txt exists

# ---------------- cache ----------------
CACHE_DIR = Path("data/.cache"); CACHE_DIR.mkdir(parents=True, exist_ok=True)

def _ckey(source: str, query: str, limit: int) -> Path:
    h = hashlib.sha1(f"{source}|{query}|{limit}".encode()).hexdigest()
    return CACHE_DIR / f"{source}.{h}.json"

def _load_cache(p: Path):
    if p.is_file():
        try: return json.loads(p.read_text(encoding="utf-8"))
        except: return None

def _save_cache(p: Path, data: list[str]):
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

def _dedupe_trim(texts: list[str], n: int) -> list[str]:
    seen, out = set(), []
    for t in texts:
        t = (t or "").strip()
        if t and t not in seen:
            seen.add(t); out.append(t)
        if len(out) >= n: break
    return out

# ---------------- Twitter via twscrape (preferred) ----------------
async def _tw_async(query: str, limit: int) -> list[str]:
    from twscrape import API
    api = API()
    # If the installed version exposes pool.load(), call it; otherwise proceed.
    try:
        if hasattr(api.pool, "load"):
            await api.pool.load()
    except Exception:
        pass

    results: list[str] = []
    async for tw in api.search(query, limit=limit):
        txt = getattr(tw, "rawContent", None) or getattr(tw, "text", None)
        if txt:
            results.append(txt)
    return results

def _fetch_twitter_twscrape(query: str, limit: int) -> list[str]:
    try:
        return asyncio.run(_tw_async(query, limit))
    except Exception as e:
        raise RuntimeError(f"twscrape failed: {e}")

# ---------------- Twitter via snscrape (fallback) ----------------
def _fetch_twitter_snscrape(query: str, limit: int, max_wait: int = 20) -> list[str]:
    start = time.time()
    out: list[str] = []
    it = sntwitter.TwitterSearchScraper(query).get_items()
    try:
        for tw in it:
            if tw.content and len(tw.content.strip()) > 3:
                out.append(tw.content)
                if len(out) >= limit:
                    break
            if not out and (time.time() - start) > max_wait:
                raise RuntimeError("snscrape timed out (no results) — likely blocked/429.")
    except Exception as e:
        raise RuntimeError(f"snscrape failed: {e}")
    return out

# ---------------- Public: Twitter ----------------
def fetch_twitter_posts(query: str, limit: int = 50) -> List[str]:
    # Force English and keep first pull light to reduce bans
    if "lang:" not in query:
        query = f"{query} lang:en"
    limit = max(5, min(limit, 50))

    # cache
    cpath = _ckey("twitter", query, limit)
    cached = _load_cache(cpath)
    if cached:
        return cached[:limit]

    # 1) twscrape
    try:
        texts = _fetch_twitter_twscrape(query, limit)
        texts = _dedupe_trim(texts, limit)
        if texts:
            _save_cache(cpath, texts)
            return texts
    except Exception as e1:
        tw_err = e1
    else:
        tw_err = None

    # 2) snscrape
    try:
        texts = _fetch_twitter_snscrape(query, limit)
        texts = _dedupe_trim(texts, limit)
        if texts:
            _save_cache(cpath, texts)
            return texts
    except Exception as e2:
        sn_err = e2
        pass

    raise RuntimeError(f"Twitter blocked both scrapers. twscrape: {tw_err} | snscrape: {sn_err}")

# ---------------- Reddit via PRAW (official API) ----------------
def _fetch_reddit_praw(query: str, limit: int) -> list[str]:
    import praw
    cid = os.getenv("REDDIT_CLIENT_ID")
    csec = os.getenv("REDDIT_CLIENT_SECRET")
    uag = os.getenv("REDDIT_USER_AGENT", "sentiment-dashboard/0.1")

    if not (cid and csec):
        raise RuntimeError("Missing Reddit API credentials (REDDIT_CLIENT_ID/SECRET).")

    reddit = praw.Reddit(client_id=cid, client_secret=csec, user_agent=uag, check_for_async=False)

    out: list[str] = []
    for s in reddit.subreddit("all").search(query, sort="new", limit=limit):
        title = getattr(s, "title", "") or ""
        body  = getattr(s, "selftext", "") or ""
        t = f"{title} {body}".strip()
        if len(t) > 3:
            out.append(t)
    return out

# ---------------- Reddit via snscrape (fallback) ----------------
def _fetch_reddit_snscrape(query: str, limit: int) -> list[str]:
    posts: list[str] = []
    for i, sub in enumerate(snreddit.RedditSearchScraper(query).get_items()):
        if i >= limit: break
        text = f"{getattr(sub,'title','') or ''} {getattr(sub,'selftext','') or ''}".strip()
        if len(text) > 3:
            posts.append(text)
    return posts

# ---------------- Public: Reddit ----------------
def fetch_reddit_posts(query: str, limit: int = 50) -> List[str]:
    cpath = _ckey("reddit", query, limit)
    cached = _load_cache(cpath)
    if cached:
        return cached[:limit]

    try:
        posts = _fetch_reddit_praw(query, limit)
        posts = _dedupe_trim(posts, limit)
        if posts:
            _save_cache(cpath, posts)
            return posts
    except Exception as e_api:
        api_err = e_api
    else:
        api_err = None

    try:
        posts = _fetch_reddit_snscrape(query, limit)
        posts = _dedupe_trim(posts, limit)
        if posts:
            _save_cache(cpath, posts)
            return posts
    except Exception as e_scr:
        scr_err = e_scr
        pass

    raise RuntimeError(f"Reddit fetch failed. praw: {api_err} | snscrape: {scr_err}")
