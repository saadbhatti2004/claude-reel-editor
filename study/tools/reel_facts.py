"""One line of facts about a reference reel for its analyst's prompt: date, length, fps, views, x median, likes,
comments, the caption's first line. usage: python reel_facts.py <work_root> <creator>/<shortcode> ..."""
import json, os, subprocess, sys

root, items = sys.argv[1], sys.argv[2:]
cache = {}
for it in items:
    creator, code = it.split('/')
    if creator not in cache:
        posts = json.load(open(os.path.join(root, 'profiles', f'{creator}.posts.json'), encoding='utf-8'))
        vids = sorted(p['videoViewCount'] for p in posts if p.get('type') == 'Video' and p.get('videoViewCount'))
        cache[creator] = ({p['shortCode']: p for p in posts}, vids[len(vids) // 2])
    P, med = cache[creator]
    p = P.get(code, {})
    d = os.path.join(root, creator, code, 'video.mp4')
    pr = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=avg_frame_rate',
                         '-show_entries', 'format=duration', '-of', 'csv=p=0', d], capture_output=True, text=True).stdout.split()
    fps = pr[0] if pr else '?'
    dur = float(pr[1]) if len(pr) > 1 else 0
    v = p.get('videoViewCount') or 0
    cap = (p.get('caption') or '').strip().splitlines()
    print(f"{it} | posted {(p.get('timestamp') or '')[:10]} | {dur:.1f} s | {fps} fps | {v} views ({v / med:.1f}x median {med}) "
          f"| {p.get('likesCount')} likes | {p.get('commentsCount')} comments | caption opens: {(cap[0] if cap else '')[:90]}")
