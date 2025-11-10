from pathlib import Path

infile = Path('twitter_cookies.txt')
raw = infile.read_text(encoding='utf-8').splitlines()

out = []
for ln in raw:
    if not ln.strip() or ln.startswith('#'):
        continue
    parts = ln.split('\t')
    if len(parts) < 7:
        continue
    # remove #HttpOnly_ prefix
    parts[0] = parts[0].replace('#HttpOnly_', '')
    # ensure domain begins with dot
    if not parts[0].startswith('.'):
        parts[0] = '.' + parts[0]
    out.append('\t'.join(parts))

Path('twitter_cookies_clean.txt').write_text('\n'.join(out) + '\n')
print("✅ Clean file written: twitter_cookies_clean.txt (", len(out), "cookies )")
