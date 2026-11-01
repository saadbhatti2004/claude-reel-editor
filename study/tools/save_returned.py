"""Save an analyst's returned report (the text it handed back) as a study document in the repo.
Keeps everything from the first line that STARTS with '# ANALYSIS', '# SCAN' or '# PROFILE'; a short summary the analyst
put before it is kept too, moved under the title. Long and short dashes are replaced (the repo is dash-free).
usage: python save_returned.py <returned text file> <out .md>"""
import re, sys

NL = chr(10)
EM, EN = chr(0x2014), chr(0x2013)

src, out = sys.argv[1], sys.argv[2]
t = open(src, encoding='utf-8').read()
m = re.search(r'(?m)^# (ANALYSIS|SCAN|PROFILE):', t) or re.search(r'(?m)^# (ANALYSIS|SCAN|PROFILE)', t)   # the titled line wins over a bare preamble one
if not m:
    sys.exit('no line starting with "# ANALYSIS", "# SCAN" or "# PROFILE" in ' + src)
head, body = t[:m.start()], t[m.start():]
s = re.search(r'(?im)^\s*(?:#+\s*)?\**\d+-line summary\**:?\s*$', head)
if s:
    summary = head[s.end():].strip()
    title, _, rest = body.partition(NL)
    body = title + NL + NL + "## Summary (the analyst's own)" + NL + NL + summary + NL + rest
body = body.replace(EM, ', ').replace(EN, ' to ').rstrip() + NL
open(out, 'w', encoding='utf-8').write(body)
print(out, len(body), 'chars,', body.count(NL + '## '), 'sections')
