#!/usr/bin/env bash
# Fetch the make.fun press files this ad uses, verifying sha256 from the manifest.
set -euo pipefail
mkdir -p press
curl -s -o press-manifest.json https://make.fun/press/manifest.json
cd press
for u in \
 "https://make.fun/press/brand-badge/9x16/makefun-badge-9x16.png" \
 "https://make.fun/press/referral-card/9x16/makefun-card-9x16-transparent.webm" \
 "https://make.fun/press/illustrations/ghost-pile-trophy.png" \
 "https://make.fun/press/illustrations/ghost-laptop-recording.png" \
 "https://make.fun/press/illustrations/ghost-wave-mail.png" \
 "https://make.fun/press/screenshots/board-dark.png" \
 "https://make.fun/press/screenshots/competition-dark.png" \
 "https://make.fun/press/referral-card/stills/3-wordmark.png" ; do
  curl -s -O "$u"
done
cd ..
python3 - <<'PYEOF'
import json, hashlib, os
m = json.load(open('press-manifest.json'))
want = {}
def walk(o):
    if isinstance(o, dict):
        if 'sha256' in o and 'path' in o:
            want[o['path'].split('/')[-1]] = o['sha256']
        for v in o.values(): walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
walk(m)
for f in sorted(os.listdir('press')):
    h = hashlib.sha256(open(os.path.join('press', f), 'rb').read()).hexdigest()
    assert h == want[f], f'sha256 mismatch: {f}'
    print(f, 'OK')
PYEOF
