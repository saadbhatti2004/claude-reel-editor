"""Pull an agent's final report out of its transcript into a plain text file, without printing it. Use when a report
came back inline (not saved as a tool-results file). The transcript is
~/.claude/projects/<project>/<session>/subagents/agent-<id>.jsonl (the task's .output file can be empty).
The report is either an assistant text block or the `message` of its SubagentHandback call; the last long one wins.
usage: python extract_final.py <agent .jsonl> <out.txt> [marker, default '# ']"""
import json, sys

src, out = sys.argv[1], sys.argv[2]
marker = sys.argv[3] if len(sys.argv) > 3 else '# '
best = None
for line in open(src, encoding='utf-8'):
    try:
        d = json.loads(line)
    except Exception:
        continue
    m = d.get('message') or {}
    if m.get('role') != 'assistant':
        continue
    c = m.get('content')
    parts = [c] if isinstance(c, str) else []
    for x in (c if isinstance(c, list) else []):
        if not isinstance(x, dict):
            continue
        if x.get('type') == 'text':
            parts.append(x.get('text', ''))
        elif x.get('type') == 'tool_use' and isinstance((x.get('input') or {}).get('message'), str):
            parts.append(x['input']['message'])
    for txt in parts:
        if marker in txt and len(txt) > 3000:
            best = txt
if not best:
    sys.exit('no long assistant text with the marker')
open(out, 'w', encoding='utf-8').write(best)
print(out, len(best), 'chars')
