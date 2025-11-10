from pathlib import Path

src = Path('twitter_cookies.txt').read_text(encoding='utf-8').splitlines()

rows = []
for ln in src:
    if not ln.strip() or ln.startswith('#'):
        continue
    parts = ln.split('\t')
    if len(parts) < 7:
        continue
    # strip #HttpOnly_
    parts[0] = parts[0].replace('#HttpOnly_', '')
    # ensure leading dot
    if not parts[0].startswith('.'):
        parts[0] = '.' + parts[0]
    rows.append('\t'.join(parts))

# duplicate all cookies for .x.com too
rows2 = []
for ln in rows:
    rows2.append(ln)
    p = ln.split('\t')
    p[0] = p[0].replace('.twitter.com', '.x.com')
    rows2.append('\t'.join(p))

Path('twitter_cookies_merged.txt').write_text('\n'.join(rows2) + '\n', encoding='utf-8')
print('✅ Wrote twitter_cookies_merged.txt with', len(rows2), 'rows')
