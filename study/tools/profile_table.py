"""Turn a scraped profile (a scraped list of posts) into a readable post table for the study, newest first.
usage: python profile_table.py <profilesDir> <handle> <outMd> [<shortcode marked as a deep-study pick> ...]
"""
import json, os, sys
from datetime import datetime

pdir, handle, out, *picks = sys.argv[1:]
posts = json.load(open(os.path.join(pdir, f'{handle}.posts.json'), encoding='utf-8'))
det = json.load(open(os.path.join(pdir, f'{handle}.details.json'), encoding='utf-8')) or {}
posts.sort(key=lambda p: p.get('timestamp') or '', reverse=True)

vids = [p for p in posts if p.get('type') == 'Video' and p.get('videoViewCount')]
med = sorted(p['videoViewCount'] for p in vids)[len(vids) // 2] if vids else 0

def first_line(c):
    c = (c or '').strip().splitlines()
    return (c[0] if c else '').replace('|', '/').replace(chr(0x2014), ',').replace(chr(0x2013), ' to ')[:110]

rows = []
for p in posts:
    v = p.get('videoViewCount') or 0
    x = f'{v / med:.1f}x' if med and v else ''
    rows.append(f"| {(p.get('timestamp') or '')[:10]} | [{p['shortCode']}](https://www.instagram.com/p/{p['shortCode']}/) "
                f"| {'**deep**' if p['shortCode'] in picks else ''} | {p.get('type')} | {v or ''} | {x} | {p.get('likesCount', '')} "
                f"| {p.get('commentsCount', '')} | {'pinned' if p.get('isPinned') else ''}{' paid' if p.get('paidPartnership') else ''} | {first_line(p.get('caption'))} |")

bio = (det.get('biography') or '').replace('\n', ' / ')
md = [f"# @{handle}: every post scraped on {datetime.now():%Y-%m-%d}",
      '',
      f"- **Name:** {det.get('fullName')} · **followers:** {det.get('followersCount')} · **posts on the profile:** {det.get('postsCount')} · **verified:** {det.get('verified')}",
      f"- **Bio:** {bio}",
      f"- **Link in bio:** {det.get('externalUrl')}",
      f"- **Scraped:** {len(posts)} most recent posts ({sum(p.get('type') == 'Video' for p in posts)} videos). Median video views {med}; x = views against that median.",
      '',
      '| Date | Post | Pick | Type | Views | x median | Likes | Comments | Flags | Caption, first line |',
      '|---|---|---|---|---|---|---|---|---|---|'] + rows
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, 'w', encoding='utf-8').write('\n'.join(md) + '\n')
print(out, len(rows), 'rows; median views', med)
