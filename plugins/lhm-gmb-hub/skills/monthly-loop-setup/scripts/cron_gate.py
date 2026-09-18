"""Hermes no-agent trigger. No research, writes to clients or email here."""
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

at = datetime.now(ZoneInfo('Australia/Melbourne'))
if at.weekday() == 0 and at.hour == 12 and 15 <= at.minute < 25:
    root = Path('/opt/data/profiles/lhm_brain/dispatch/seo-weekly/incoming')
    root.mkdir(parents=True, exist_ok=True)
    path = root / (at.date().isoformat() + '.json')
    try:
        with path.open('x') as f:
            json.dump({'mode': 'production', 'week': at.date().isoformat()}, f)
        print(json.dumps({'state': 'queued', 'week': at.date().isoformat()}))
    except FileExistsError:
        pass
