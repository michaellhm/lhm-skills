#!/usr/bin/env python3
"""Independent deterministic watchdog. Reconciles receipts; never starts model work."""
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo('Australia/Melbourne')
CONFIG = Path('/etc/lhm-weekly-web-brief.json')


def read(path):
    return json.loads(path.read_text()) if path.exists() else {}


def decision(at, status, receipt, service, started=None):
    """Return one fixed reason; no arbitrary exception or client content enters alerts."""
    if receipt.get('state') == 'delivered':
        return None
    if receipt:
        state = receipt.get('state')
        if state == 'failed':
            return 'delivery_failed'
        if state in ('delivery_uncertain', 'sending'):
            # A persisted intent cannot authorize a second send, even after a crash.
            return 'delivery_uncertain' if state == 'delivery_uncertain' or service not in ('activating', 'active') else None
        if state == 'queued':
            sent = datetime.fromisoformat(receipt['started_at'])
            return 'delivery_pending' if (at - sent).total_seconds() >= 1200 else None
    if status.get('state') == 'failed':
        return status.get('failure_reason', 'quality_blocked' if status.get('error', '').startswith('Independent review rejected:') else 'worker_failed')
    if status.get('state') == 'running':
        began = status.get('started_at')
        began = datetime.fromisoformat(began) if began else started
        if began and (at - began).total_seconds() >= 10800:
            return 'timeout'
        if service not in ('activating', 'active'):
            return 'interrupted'
        return None
    if service == 'failed':
        return 'worker_failed'
    due = at.replace(hour=12, minute=15, second=0, microsecond=0) - timedelta(days=at.weekday())
    if at >= due and not status:
        return 'missed_start'
    return None


def sender(action, week, reason=None):
    cmd = ['docker', 'exec', '-u', 'hermes', 'hermes', '/opt/data/.venv/bin/python',
           '/opt/data/profiles/lhm_brain/skills/weekly-web-project-brief/scripts/brief.py', action, '--week', week]
    if action == 'alert':
        cmd += ['--reason', reason]
    elif action == 'verify-alert':
        cmd[cmd.index(action)] = 'verify'; cmd += ['--kind', 'alert']
    result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=60)
    return json.loads(result.stdout)


def check(cfg, at=None):
    at = (at or datetime.now(TZ)).astimezone(TZ)
    week = (at.date() - timedelta(days=at.weekday())).isoformat()
    if week < cfg['watch_from_week'] or (at.weekday() == 0 and at.hour < 12):
        return {'state': 'outside_watch_window'}
    root = Path(cfg['state'])
    status_path = root / 'runtime' / week / 'status.json'
    receipt_path = root / 'receipts' / (week + '-brief.json')
    status = read(status_path); receipt = read(receipt_path)
    # Reconcile pending provider state before declaring delivery missing.
    if receipt.get('message_id') and receipt.get('state') not in ('delivered', 'failed'):
        try:
            sender('verify', week); receipt = read(receipt_path)
        except (subprocess.SubprocessError, ValueError):
            # Provider read outages never authorize resend; retain the pending state.
            pass
    service = subprocess.run(['systemctl', 'show', 'lhm-weekly-web-brief.service',
                              '--property=ActiveState', '--value'], capture_output=True, text=True, check=True).stdout.strip()
    started = datetime.fromtimestamp(status_path.stat().st_mtime, TZ) if status_path.exists() else None
    reason = decision(at, status, receipt, service, started)
    if reason:
        result = sender('alert', week, reason)
        if result.get('state') != 'brief_already_delivered':
            result = sender('verify-alert', week)
        return {'state': 'attention_required', 'reason': reason, 'notification': result}
    return {'state': 'healthy_or_in_progress', 'week': week}


if __name__ == '__main__':
    print(json.dumps(check(json.loads(CONFIG.read_text()))))
