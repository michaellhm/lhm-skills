#!/usr/bin/env python3
"""
Build the interactive proposed-sitemap HTML page from a JSON spec.

Usage:
    python build_sitemap_html.py sitemap.json output.html

The JSON spec is documented in references/sitemap-schema.md. A complete worked
example is in assets/example-sitemap.json. Nothing about the design is hard-coded
to a particular client. Brand colours, logo, nav, sections and the opportunity
model all come from the JSON, so the same script renders a consistent, branded
page for any client.

Two modes, chosen by the JSON:

    "opportunity": {...}   -> prospect mode. Renders the impressions-to-leads
                              widget with editable CTR/conversion and the
                              ongoing-SEO slider above the page tree.
    (key absent or null)   -> client mode. Renders the page tree only. No widget,
                              no calculator JavaScript, no lead estimates.

Status values on pages / nav items:
    "have"  -> green  (client already has this page)
    "enh"   -> yellow (exists, should be rebuilt/expanded)
    "new"   -> red    (does not exist yet, the opportunity)

NOTE: this file is duplicated in the client-sitemap-plan skill. The two copies are
identical by design. If you change one, change both.
"""
import json, sys, html

def esc(s):
    return html.escape(str(s), quote=True)

# ----------------------------------------------------------------------------- CSS
CSS = """
  :root{
    --green:__PRIMARY__; --green-d:__PRIMARY_DARK__; --lgreen:__PRIMARY_LIGHT__; --gold:__ACCENT__;
    --dark:#1F2D23; --grey:#5B6B60; --line:#D8E0D8; --bg:#F6F8F5;
    --have:#2E7D32;  --have-bg:#E4EFE7;
    --enh:#E0A100;   --enh-bg:#FBF0D2;   --enh-txt:#9A6E00;
    --new:#C62828;   --new-bg:#FBE3E3;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
       color:var(--dark);background:var(--bg);line-height:1.5;-webkit-font-smoothing:antialiased}
  header.site{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:50;box-shadow:0 1px 4px rgba(0,0,0,.04)}
  .bar{max-width:1240px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;padding:14px 22px;gap:16px}
  .logo{display:flex;align-items:center;gap:10px;font-weight:800;color:var(--green);font-size:19px;letter-spacing:-.01em;flex:0 0 auto}
  .logo img{height:36px;width:auto}
  nav.top>ul{list-style:none;display:flex;gap:1px;align-items:center;flex-wrap:nowrap}
  nav.top>ul>li{position:relative}
  nav.top>ul>li>a{display:block;padding:10px 10px;text-decoration:none;color:var(--dark);font-size:13.5px;font-weight:600;border-radius:7px;white-space:nowrap}
  nav.top>ul>li:hover>a{background:var(--lgreen);color:var(--green-d)}
  nav.top>ul>li .caret{font-size:10px;color:var(--grey);margin-left:4px}
  .dropdown{position:absolute;top:100%;left:0;background:#fff;border:1px solid var(--line);border-radius:10px;box-shadow:0 10px 30px rgba(0,0,0,.12);min-width:250px;padding:6px;opacity:0;visibility:hidden;transform:translateY(6px);transition:.14s;z-index:60}
  nav.top>ul>li:hover .dropdown{opacity:1;visibility:visible;transform:translateY(3px)}
  .dropdown a{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:8px 10px;border-radius:7px;text-decoration:none;color:var(--dark);font-size:13.5px}
  .dropdown a:hover{background:var(--lgreen)}
  .dropdown .grp{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--grey);padding:9px 10px 4px}
  .dropdown.mega{display:grid;grid-template-columns:repeat(var(--cols,3),minmax(165px,185px));gap:4px 8px;width:max-content;max-width:96vw;padding:10px}
  .mega .col{display:flex;flex-direction:column}
  .mega .grp{border-bottom:1px solid var(--line);margin-bottom:2px}
  .callbtn{background:var(--green);color:#fff;padding:9px 15px;border-radius:8px;font-weight:700;font-size:14px;white-space:nowrap;text-decoration:none}
  .dot{width:9px;height:9px;border-radius:50%;flex:0 0 auto;display:inline-block;vertical-align:middle}
  .dot.new{background:var(--new)} .dot.enh{background:var(--enh)} .dot.have{background:var(--have)}
  .wrap{max-width:1240px;margin:0 auto;padding:26px 22px 60px}
  .opp{background:linear-gradient(180deg,#12351f 0%, var(--green-d) 100%);border-radius:16px;padding:22px 24px 20px;color:#fff;margin-bottom:24px;box-shadow:0 12px 34px rgba(18,53,31,.28)}
  .opp h2{font-size:19px;letter-spacing:-.01em;margin-bottom:3px}
  .opp .sub{color:#BFE0C8;font-size:13px;max-width:820px}
  .scen{display:grid;grid-template-columns:1fr auto 1fr auto 1fr;align-items:stretch;gap:10px;margin:18px 0 4px}
  .sc{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.14);border-radius:12px;padding:14px 15px;display:flex;flex-direction:column;gap:8px}
  .sc.win{background:rgba(122,193,140,.16);border-color:rgba(122,193,140,.5)}
  .sc.seo{background:rgba(200,164,77,.16);border-color:rgba(200,164,77,.55)}
  .sc .lab{font-size:11px;text-transform:uppercase;letter-spacing:.07em;color:#CFE3D4;font-weight:700}
  .sc.seo .lab{color:#F0DDB0}
  .sc .leads{font-size:40px;font-weight:800;line-height:1;letter-spacing:-.02em}
  .sc .leadu{font-size:12px;color:#CFE3D4;margin-top:-4px}
  .sc .chain{font-size:12px;color:#DDEbe0;border-top:1px dashed rgba(255,255,255,.22);padding-top:7px;margin-top:2px}
  .sc .chain b{color:#fff}
  .arrow{display:flex;align-items:center;justify-content:center;color:#9FC7AC;font-size:22px;font-weight:800}
  .controls{display:flex;flex-wrap:wrap;gap:16px 22px;align-items:flex-end;margin-top:16px;background:rgba(0,0,0,.16);border-radius:12px;padding:14px 16px}
  .ctrl{display:flex;flex-direction:column;gap:4px}
  .ctrl label{font-size:10.5px;text-transform:uppercase;letter-spacing:.05em;color:#BFE0C8;font-weight:700}
  .ctrl input[type=number]{width:96px;background:#fff;border:1px solid rgba(255,255,255,.3);border-radius:7px;padding:7px 9px;font-size:14px;font-weight:700;color:var(--dark)}
  .seowrap{flex:1 1 320px;min-width:280px}
  .seowrap .top{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:4px}
  .seowrap .top b{font-size:13px;color:#fff}
  .seowrap .top span{font-size:12px;color:#F0DDB0;font-weight:700}
  input[type=range]{width:100%;accent-color:var(--gold);height:22px}
  .seed{font-size:12.5px;color:#CFE3D4;margin-top:12px;padding-top:11px;border-top:1px solid rgba(255,255,255,.14)}
  .seed b{color:#F0DDB0}
  .fine{font-size:10.5px;color:#9FC0A8;margin-top:9px;line-height:1.45}
  .intro{background:#fff;border:1px solid var(--line);border-radius:14px;padding:18px 22px;margin-bottom:22px}
  .intro h1{font-size:20px;color:var(--green-d);margin-bottom:5px;letter-spacing:-.01em}
  .intro p{color:var(--grey);font-size:14px;max-width:960px}
  .meta{margin-top:13px;display:flex;gap:24px;flex-wrap:wrap}
  .meta div{font-size:13px;color:var(--grey)}
  .meta b{display:block;font-size:21px;color:var(--green-d);font-weight:800;line-height:1.1}
  .legend{display:flex;gap:16px;flex-wrap:wrap;margin-top:14px;padding-top:13px;border-top:1px solid var(--line);font-size:13px;color:var(--grey)}
  .legend span{display:inline-flex;align-items:center;gap:7px}
  h2.sec{font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:var(--green);margin:26px 4px 12px;font-weight:800;display:flex;align-items:center;gap:10px}
  h2.sec:after{content:"";flex:1;height:1px;background:var(--line)}
  .cols{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:16px}
  .card{background:#fff;border:1px solid var(--line);border-radius:12px;overflow:hidden;display:flex;flex-direction:column}
  .card>.head{padding:11px 15px;background:var(--green);color:#fff;font-weight:700;font-size:14.5px;display:flex;align-items:center;justify-content:space-between;gap:8px}
  .card>.head .u{font-weight:500;font-size:11px;color:#CFE3D4;font-family:ui-monospace,Menlo,monospace}
  .card ul{list-style:none;padding:6px}
  .card li{display:flex;align-items:flex-start;gap:9px;padding:7px 9px;border-radius:7px;font-size:13.5px}
  .card li:hover{background:#F3F7F3}
  .card li .t{flex:1}
  .card li .u2{font-family:ui-monospace,Menlo,monospace;font-size:10.5px;color:var(--grey);display:block;margin-top:1px}
  .vol{font-size:11px;font-weight:700;color:var(--green-d);background:var(--lgreen);border-radius:20px;padding:1px 8px;white-space:nowrap;align-self:flex-start;margin-top:1px}
  .vol.na{color:#93A499;background:#EFF2EF;font-weight:600}
  .tag{font-size:9.5px;font-weight:800;text-transform:uppercase;letter-spacing:.04em;padding:2px 7px;border-radius:5px;align-self:flex-start;margin-top:1px;white-space:nowrap}
  .tag.new{background:var(--new-bg);color:var(--new)} .tag.enh{background:var(--enh-bg);color:var(--enh-txt)} .tag.have{background:var(--have-bg);color:var(--have)}
  .note{font-size:12.5px;color:var(--grey);background:#fff;border:1px dashed var(--line);border-radius:10px;padding:12px 15px;margin-top:12px}
  footer{max-width:1240px;margin:0 auto;padding:0 22px 40px;color:var(--grey);font-size:12px}
  .pill{display:inline-block;background:var(--new);color:#fff;font-size:11px;font-weight:700;padding:2px 9px;border-radius:20px;margin-left:8px;vertical-align:middle}
"""

STATUS_TAG = {"have": ("have", "Existing"), "enh": ("enh", "Enhance"), "new": ("new", "New")}

NEWDOT = ' <span class="dot new"></span>'

def _link(i):
    """A single dropdown link, with a red dot if the item is new."""
    dot = NEWDOT if i.get("new") else ""
    return '<a href="#">' + esc(i["label"]) + dot + '</a>'

def nav_item(item):
    label = esc(item["label"])
    newdot = NEWDOT if item.get("new") else ""
    # mega dropdown (grouped columns)
    if item.get("mega") and item.get("groups"):
        cols = len(item["groups"])
        inner = []
        for g in item["groups"]:
            links = "".join(_link(i) for i in g["items"])
            inner.append(f'<div class="col"><div class="grp">{esc(g["title"])}</div>{links}</div>')
        dd = f'<div class="dropdown mega" style="--cols:{cols}">{"".join(inner)}</div>'
        return f'<li><a href="#">{label}{newdot} <span class="caret">▾</span></a>{dd}</li>'
    # simple dropdown (flat or grouped)
    if item.get("items") or item.get("groups"):
        parts = []
        if item.get("groups"):
            for g in item["groups"]:
                parts.append(f'<div class="grp">{esc(g["title"])}</div>')
                for i in g["items"]:
                    d = NEWDOT if i.get("new") else ""
                    parts.append(f'<a href="#">{esc(i["label"])}{d}</a>')
        else:
            for i in item["items"]:
                d = NEWDOT if i.get("new") else ""
                parts.append(f'<a href="#">{esc(i["label"])}{d}</a>')
        dd = f'<div class="dropdown">{"".join(parts)}</div>'
        return f'<li><a href="#">{label}{newdot} <span class="caret">▾</span></a>{dd}</li>'
    # plain link
    return f'<li><a href="#">{label}{newdot}</a></li>'

def page_li(p):
    status = p.get("status", "new")
    cls, word = STATUS_TAG.get(status, ("new", "New"))
    name = esc(p["name"])
    if p.get("bold"):
        name = f"<b>{name}</b>"
    slug = f'<span class="u2">{esc(p["slug"])}</span>' if p.get("slug") else ""
    vol = p.get("vol", None)
    if vol in (None, "", 0):
        volhtml = '<span class="vol na">n/a</span>'
    else:
        try:
            volhtml = f'<span class="vol">{int(vol):,}</span>'
        except (ValueError, TypeError):
            volhtml = f'<span class="vol">{esc(vol)}</span>'
    return (f'<li><span class="dot {cls}"></span>'
            f'<span class="t">{name} {slug}</span>'
            f'{volhtml}<span class="tag {cls}">{word}</span></li>')

def card_html(c):
    head_u = f' <span class="u">{esc(c["url"])}</span>' if c.get("url") else ""
    items = "".join(page_li(p) for p in c["items"])
    return f'<div class="card"><div class="head">{esc(c["head"])}{head_u}</div><ul>{items}</ul></div>'

def section_html(s):
    pill = f' <span class="pill">{esc(s["pill"])}</span>' if s.get("pill") else ""
    cards = "".join(card_html(c) for c in s["cards"])
    note = f'<div class="note">{s["note"]}</div>' if s.get("note") else ""
    return f'<h2 class="sec">{esc(s["title"])}{pill}</h2><div class="cols">{cards}</div>{note}'

def opportunity_html(o):
    """The impressions -> clicks -> leads widget. Prospect mode only."""
    return f"""
  <section class="opp">
    <h2>{esc(o.get('title','The opportunity in Google Search'))}</h2>
    <div class="sub">{o.get('sub','How many enquiries the website can realistically generate from organic search, today versus with the new structure. Every number below is editable, so adjust them live and the leads recalculate.')}</div>
    <div class="scen">
      <div class="sc">
        <div class="lab">Today · current structure</div>
        <div class="leads" id="leadsNow">0</div>
        <div class="leadu">leads / month · <span id="leadsNowYr">0/yr</span></div>
        <div class="chain"><b id="impNowT">0</b> searches → <b id="clkNow">0</b> clicks → <b id="leadsNow2">0</b> leads</div>
      </div>
      <div class="arrow">→</div>
      <div class="sc win">
        <div class="lab">New website · same rates</div>
        <div class="leads" id="leadsNew">0</div>
        <div class="leadu">leads / month · <span id="leadsNewYr">0/yr</span></div>
        <div class="chain"><b id="impNewT">0</b> searches → <b id="clkNew">0</b> clicks → <b id="leadsNew2">0</b> leads</div>
      </div>
      <div class="arrow">→</div>
      <div class="sc seo">
        <div class="lab">New website + ongoing SEO</div>
        <div class="leads" id="leadsSeo">0</div>
        <div class="leadu">leads / month · <span id="leadsSeoYr">0/yr</span></div>
        <div class="chain"><b id="impSeoT">0</b> searches → <b id="clkSeo">0</b> clicks → <b id="leadsSeo2">0</b> leads</div>
      </div>
    </div>
    <div class="controls">
      <div class="ctrl"><label>Current searches / mo</label><input type="number" id="impNow" value="{int(o['imp_now'])}" min="0" step="50"></div>
      <div class="ctrl"><label>New searches / mo</label><input type="number" id="impNew" value="{int(o['imp_new'])}" min="0" step="50"></div>
      <div class="ctrl"><label>Click-through rate %</label><input type="number" id="ctr" value="{o['ctr']}" min="0" step="0.5"></div>
      <div class="ctrl"><label>Conversion rate %</label><input type="number" id="conv" value="{o['conv']}" min="0" step="0.5"></div>
      <div class="seowrap">
        <div class="top"><b>Ongoing SEO</b> <span id="seoLabel">off</span></div>
        <input type="range" id="seo" min="0" max="{int(o.get('seo_max',10))}" value="0" step="1">
        <div class="fine">Each step of ongoing SEO ≈ +{int(o.get('seo_step_pct',10))}% impressions and +{int(o.get('seo_step_pct',10))}% conversion rate (click-through held flat to stay conservative, since in practice it improves too).</div>
      </div>
    </div>
    <div class="seed">{o.get('seed','Drag the SEO slider to see how ongoing optimisation compounds the result. <b>The website gets you the structure; SEO keeps growing what it captures.</b>')}</div>
    <div class="fine">{o.get('composition_note','Illustrative model. "Searches" = average monthly search volume for the terms each structure is built to rank for.')}</div>
  </section>
"""

def opportunity_js(o):
    """Calculator for the widget. Only emitted when an opportunity block exists."""
    return f"""<script>
  const $ = id => document.getElementById(id);
  const fmt = n => Math.round(n).toLocaleString();
  const leadFmt = n => (n >= 20 ? Math.round(n).toLocaleString() : n.toFixed(1));
  const STEP = {float(o.get('seo_step_pct',10))/100};
  function calc(){{
    const impNow=+$('impNow').value||0, impNew=+$('impNew').value||0;
    const ctr=(+$('ctr').value||0)/100, conv=(+$('conv').value||0)/100;
    const steps=+$('seo').value||0, boost=1+STEP*steps;
    const ldNow=impNow*ctr*conv, clkNow=impNow*ctr;
    const ldNew=impNew*ctr*conv, clkNew=impNew*ctr;
    const impSeo=impNew*boost, convSeo=conv*boost, clkSeo=impSeo*ctr, ldSeo=clkSeo*convSeo;
    $('impNowT').textContent=fmt(impNow);$('clkNow').textContent=fmt(clkNow);
    $('leadsNow').textContent=leadFmt(ldNow);$('leadsNow2').textContent=leadFmt(ldNow);$('leadsNowYr').textContent=fmt(ldNow*12)+'/yr';
    $('impNewT').textContent=fmt(impNew);$('clkNew').textContent=fmt(clkNew);
    $('leadsNew').textContent=leadFmt(ldNew);$('leadsNew2').textContent=leadFmt(ldNew);$('leadsNewYr').textContent=fmt(ldNew*12)+'/yr';
    $('impSeoT').textContent=fmt(impSeo);$('clkSeo').textContent=fmt(clkSeo);
    $('leadsSeo').textContent=leadFmt(ldSeo);$('leadsSeo2').textContent=leadFmt(ldSeo);$('leadsSeoYr').textContent=fmt(ldSeo*12)+'/yr';
    $('seoLabel').textContent = steps===0 ? 'off' : ('+'+Math.round(steps*STEP*100)+'% traffic · +'+Math.round(steps*STEP*100)+'% conversion');
  }}
  ['impNow','impNew','ctr','conv','seo'].forEach(id=>$(id).addEventListener('input',calc));
  calc();
</script>"""

def build(spec):
    b = spec["brand"]
    primary = b.get("primary", "#2E6B3E")
    css = (CSS.replace("__PRIMARY__", primary)
              .replace("__PRIMARY_DARK__", b.get("primary_dark", "#1F4D2C"))
              .replace("__PRIMARY_LIGHT__", b.get("primary_light", "#E4EFE7"))
              .replace("__ACCENT__", b.get("accent", "#C8A44D")))
    nav = "".join(nav_item(i) for i in spec["nav"])
    logo = (f'<img src="{esc(b["logo_url"])}" alt="{esc(b["name"])}" onerror="this.style.display=\'none\'">'
            if b.get("logo_url") else f'<span>{esc(b["name"])}</span>')
    phone = f'<a class="callbtn" href="#">{esc(b["phone"])}</a>' if b.get("phone") else ""

    # Prospect mode when an opportunity block is present; client mode when it is not.
    o = spec.get("opportunity")
    opp_section = opportunity_html(o) if o else ""
    opp_script = opportunity_js(o) if o else ""
    title_suffix = " &amp; Opportunity" if o else ""

    stats = "".join(f'<div><b>{esc(s["n"])}</b> {esc(s["label"])}</div>' for s in spec.get("stats", []))
    sections = "".join(section_html(s) for s in spec["sections"])
    intro = spec.get("intro", {})
    footer = spec.get("footer", "")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(b['name'])} — Proposed Sitemap{title_suffix}</title>
<style>{css}</style>
</head>
<body>
<header class="site">
  <div class="bar">
    <div class="logo">{logo}</div>
    <nav class="top"><ul>{nav}</ul></nav>
    {phone}
  </div>
</header>
<div class="wrap">
{opp_section}
  <section class="intro">
    <h1>{esc(intro.get('title','Proposed website sitemap'))}</h1>
    <p>{intro.get('paragraph','')}</p>
    <div class="meta">{stats}</div>
    <div class="legend">
      <span><span class="dot have"></span> <b style="color:var(--have)">Existing</b>&nbsp;— you already have this page</span>
      <span><span class="dot enh"></span> <b style="color:var(--enh-txt)">Enhance</b>&nbsp;— exists, rebuild to rank &amp; convert</span>
      <span><span class="dot new"></span> <b style="color:var(--new)">New</b>&nbsp;— doesn't exist yet</span>
      <span>🔎 Green number = monthly searches · "n/a" = no volume recorded</span>
    </div>
  </section>

  {sections}
</div>
<footer>{footer}</footer>
{opp_script}
</body>
</html>
"""

def main():
    if len(sys.argv) < 3:
        print("Usage: python build_sitemap_html.py <sitemap.json> <output.html>")
        sys.exit(1)
    with open(sys.argv[1], encoding="utf-8") as f:
        spec = json.load(f)
    out = build(spec)
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(out)
    mode = "prospect (with opportunity widget)" if spec.get("opportunity") else "client (no widget)"
    print(f"Wrote {sys.argv[2]} — {mode}")

if __name__ == "__main__":
    main()
