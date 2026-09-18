"""Render a card-first Google Ads email; no network access or sending authority."""
import argparse
import html
import json
from pathlib import Path
from urllib.parse import urlsplit

LIGHTS = {'red': ('🔴', 'Red', '#b42318', '#fff1f0'), 'orange': ('🟠', 'Orange', '#a04c00', '#fff5e9'), 'green': ('🟢', 'Green', '#17643b', '#edf8ef'), 'yellow': ('🟡', 'Yellow', '#806000', '#fffbe6'), 'blue': ('🔵', 'Blue', '#175a96', '#edf5ff'), 'unknown': ('⚪', 'Unverified', '#526070', '#f1f4f6')}

def render(data):
    cards = []
    plain = [data['heading'], data['intro']]
    for c in data['clients']:
        light = 'orange' if c['light'].lower() == 'amber' else c['light'].lower()
        emoji, label, color, bg = LIGHTS[light]
        u = urlsplit(c.get('task_url') or '')
        if c.get('task_url') and (u.scheme != 'https' or u.netloc != 'app.basicops.com' or u.username or u.password or not u.query.startswith('l=')):
            raise ValueError('Expected a verified native BasicOps card URL')
        if not 1 <= len(c['highlights']) <= 4:
            raise ValueError('Each client needs one to four highlights')
        esc = html.escape
        button = ('<table role="presentation" cellspacing="0" cellpadding="0"><tr><td style="background:#18596a;border-radius:6px"><a href="'+esc(c['task_url'], quote=True)+'" style="display:inline-block;padding:12px 20px;color:#ffffff;text-decoration:none;font-weight:bold">Open review card →</a></td></tr></table>') if c.get('task_url') else '<p>Review card unavailable. Delivery needs attention.</p>'
        items = ''.join('<li style="margin:0 0 10px">'+esc(s)+'</li>' for s in c['highlights'])
        cards.append(f'''<tr><td style="padding:0 28px 24px"><table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border:1px solid #e0e6eb;border-radius:12px"><tr><td style="padding:24px">
<p style="font-size:13px;font-weight:bold;color:{color};margin:0 0 12px;background:{bg};padding:7px 10px">{emoji} {label} · {esc(c['status_reason'])}</p>
<h2 style="font-size:22px;margin:0 0 10px;color:#17354a">{esc(c['name'])}</h2>
<p style="font-size:13px;color:#536575;margin:0 0 20px">{esc(c['stage'])}</p>
<ul style="padding-left:20px;margin:0 0 20px">{items}</ul>
<p style="margin:0 0 22px"><strong>Start here:</strong> {esc(c['next_action'])}</p>
{button}
</td></tr></table></td></tr>''')
        plain += [f'{emoji} {label} | {c["name"]}', c['status_reason'], c['stage'], *['• '+s for s in c['highlights']], 'Start here: '+c['next_action'], 'Open review card: '+c['task_url'] if c.get('task_url') else 'Review card unavailable. Delivery needs attention.']
    if not cards:
        raise ValueError('Do not send an empty normal digest')
    esc = html.escape
    body = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(data['subject'])}</title></head>
<body style="margin:0;background:#eef3f5;font-family:Arial,sans-serif;color:#263a48;line-height:1.55"><table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr><td align="center" style="padding:28px 12px"><table role="presentation" width="640" cellspacing="0" cellpadding="0" style="max-width:640px;width:100%;background:white;border-radius:14px">
<tr><td style="padding:30px 28px 24px"><p style="font-size:11px;letter-spacing:2px;color:#537180;margin:0 0 10px">LOCAL HEALTH MARKETING</p><h1 style="font-size:28px;line-height:1.2;margin:0 0 12px;color:#17354a">{esc(data['heading'])}</h1><p style="margin:0;color:#536575">{esc(data['intro'])}</p></td></tr>
{''.join(cards)}
<tr><td style="padding:0 28px 28px"><p style="font-size:13px;color:#536575">{esc(data['footer'])}</p><p style="margin:18px 0 0;font-weight:bold">Lily</p><p style="font-size:12px;color:#71818d;margin:0">Local Health Marketing</p></td></tr></table></td></tr></table></body></html>'''
    return {'subject': data['subject'], 'html': body, 'text': '\n\n'.join(plain+[data['footer'], 'Lily | Local Health Marketing'])}

if __name__ == '__main__':
    p = argparse.ArgumentParser();p.add_argument('input');p.add_argument('output');a=p.parse_args()
    result=render(json.loads(Path(a.input).read_text()));out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    (out/'email.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    (out/'email.html').write_text(result['html']);(out/'email.txt').write_text(result['text'])
