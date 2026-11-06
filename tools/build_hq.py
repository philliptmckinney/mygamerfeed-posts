"""Build the static Gamer Feed HQ page (plain HTML and CSS, no scripts, so it opens on older phones).
Usage: python3 build_hq.py stats.json queue.json out.html
stats.json: {"updated", "youtube": {"subscribers", "shorts": [{title,date,views,comments}]},
             "tiktok": {"followers", "likes_total", "posts": [{post,date,views,likes,comments}]},
             "instagram": {"followers", "posts": [...]}}
queue.json: [{"due": ISO UTC, "platform", "post"}] soonest first
"""
import html, json, sys
from datetime import datetime, timezone, timedelta

def central(dt):
    # US Central: CDT (UTC-5) from 2nd Sunday of March to 1st Sunday of November, else CST (UTC-6)
    y = dt.year
    mar = datetime(y, 3, 8, 8, tzinfo=timezone.utc); mar += timedelta(days=(6 - mar.weekday()) % 7)
    nov = datetime(y, 11, 1, 7, tzinfo=timezone.utc); nov += timedelta(days=(6 - nov.weekday()) % 7)
    return dt + timedelta(hours=-5 if mar <= dt < nov else -6)

def t(dt):
    c = central(dt)
    h = c.strftime("%I").lstrip("0")
    return f"{c.strftime('%a %b')} {c.day}, {h}:{c.strftime('%M')} {c.strftime('%p').lower()}"

def n(x):
    return "" if x is None else f"{int(x):,}"

def day(s):
    d = datetime.strptime(s, "%Y-%m-%d")
    return f"{d.strftime('%b')} {d.day}"

e = html.escape
stats = json.load(open(sys.argv[1])); queue = json.load(open(sys.argv[2])); out = sys.argv[3]
up = datetime.fromisoformat(stats["updated"].replace("Z", "+00:00"))
yt, tt, ig = stats["youtube"], stats["tiktok"], stats.get("instagram", {})
subs, fol = yt.get("subscribers") or 0, tt.get("followers") or 0
days_left = max(0, (datetime(2027, 1, 31, 6, tzinfo=timezone.utc) - datetime.now(timezone.utc)).days)

rows = [("YouTube", p["title"], p["date"], p.get("views"), None, p.get("comments")) for p in yt.get("shorts", [])]
rows += [("TikTok", p["post"], p["date"], p.get("views"), p.get("likes"), p.get("comments")) for p in tt.get("posts", [])]
rows += [("Instagram", p["post"], p["date"], p.get("views"), p.get("likes"), p.get("comments")) for p in ig.get("posts", [])]
rows.sort(key=lambda r: r[2], reverse=True)
week = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
yt_week = sum(r[3] or 0 for r in rows if r[0] == "YouTube" and r[2] >= week)
tt_week = sum(r[3] or 0 for r in rows if r[0] == "TikTok" and r[2] >= week)
best = max((r for r in rows if r[2] >= week), key=lambda r: r[3] or 0, default=None)

def bar(v, goal):
    return f'<div class="bar"><i style="width:{min(100, v / goal * 100):.1f}%"></i></div>'

post_rows = "".join(
    f'<tr><td class="d">{day(r[2])}</td><td><span class="pill {r[0].lower()}">{r[0]}</span></td><td class="p">{e(r[1])}</td>'
    f'<td class="num">{n(r[3])}</td><td class="num">{n(r[4])}</td><td class="num">{n(r[5])}</td></tr>' for r in rows)
q_rows = "".join(
    f'<tr><td class="d">{t(datetime.fromisoformat(q["due"].replace("Z", "+00:00")))}</td><td><span class="pill {q["platform"].lower()}">{e(q["platform"])}</span></td><td class="p">{e(q["post"])}</td></tr>'
    for q in queue) or '<tr><td colspan="3">Nothing scheduled.</td></tr>'
best_line = f'Best this week: <b>{e(best[1])}</b> on {best[0]}, {n(best[3])} views.' if best else ""

page = f"""<title>Gamer Feed HQ</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
:root {{ --bg:#f5f4f8; --panel:#ffffff; --fg:#17151f; --muted:#5f5b6e; --line:#e2e0ea; --accent:#6c3cf0; --yt:#d6332b; --tt:#111111; --ig:#c13584; --good:#1f8a4c; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#121018; --panel:#1c1a25; --fg:#f1eff7; --muted:#a8a3b8; --line:#2e2b3a; --accent:#a78bfa; --yt:#ff6b63; --tt:#e8e8e8; --ig:#f07ac1; --good:#5fd38f; color-scheme:dark; }} }}
:root[data-theme="dark"] {{ --bg:#121018; --panel:#1c1a25; --fg:#f1eff7; --muted:#a8a3b8; --line:#2e2b3a; --accent:#a78bfa; --yt:#ff6b63; --tt:#e8e8e8; --ig:#f07ac1; --good:#5fd38f; color-scheme:dark; }}
body {{ background:var(--bg); color:var(--fg); font:15px/1.45 -apple-system, "Helvetica Neue", Arial, sans-serif; }}
.wrap {{ max-width:960px; margin:0 auto; padding-left:max(16px, env(safe-area-inset-left, 0px)); padding-right:max(16px, env(safe-area-inset-right, 0px)); padding-block:20px 40px; }}
h1 {{ font-size:26px; margin:0; letter-spacing:-.01em; }}
.lede {{ color:var(--muted); margin:6px 0 18px; }}
.lede b {{ color:var(--fg); }}
.tiles {{ display:-webkit-box; display:flex; flex-wrap:wrap; margin:0 -6px 12px; }}
.tile {{ background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:14px; margin:6px; -webkit-box-flex:1; flex:1 1 180px; min-width:0; }}
.lab {{ font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:.06em; }}
.big {{ font-size:30px; font-weight:700; margin-top:4px; font-variant-numeric:tabular-nums; }}
.sub {{ font-size:12px; color:var(--muted); margin-top:2px; }}
.bar {{ height:6px; background:var(--line); border-radius:3px; margin-top:8px; overflow:hidden; }}
.bar i {{ display:block; height:100%; background:var(--accent); border-radius:3px; }}
.card {{ background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:14px; margin-top:12px; }}
h2 {{ font-size:17px; margin:0 0 2px; }}
.note {{ font-size:12px; color:var(--muted); margin:0 0 10px; }}
.scroll {{ overflow-x:auto; -webkit-overflow-scrolling:touch; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; font-variant-numeric:tabular-nums; }}
th {{ text-align:left; font-weight:600; color:var(--muted); border-bottom:1px solid var(--line); padding:6px 8px 6px 0; white-space:nowrap; }}
td {{ border-bottom:1px solid var(--line); padding:6px 8px 6px 0; vertical-align:top; }}
.num {{ text-align:right; white-space:nowrap; }}
.d {{ white-space:nowrap; color:var(--muted); }}
.p {{ min-width:160px; }}
.pill {{ display:inline-block; font-size:11px; font-weight:600; padding:1px 7px; border-radius:999px; border:1px solid currentColor; white-space:nowrap; }}
.youtube {{ color:var(--yt); }} .tiktok {{ color:var(--tt); }} .instagram {{ color:var(--ig); }}
ul {{ margin:0; padding:0; list-style:none; }}
.links li {{ border-bottom:1px solid var(--line); padding:8px 0; }}
.links a {{ color:var(--accent); font-weight:600; text-decoration:none; }}
.links span, .auto span {{ display:block; font-size:12px; color:var(--muted); }}
.auto li {{ border-bottom:1px solid var(--line); padding:6px 0; font-size:13px; }}
</style>
<div class="wrap">
<h1>Gamer Feed HQ</h1>
<p class="lede">Updated {t(up)} Central. <b>{n(yt_week)}</b> YouTube views and <b>{n(tt_week)}</b> TikTok views on posts from the last 7 days. {best_line}</p>
<div class="tiles">
 <div class="tile"><div class="lab">YouTube subscribers</div><div class="big">{n(subs)}</div>{bar(subs, 1000)}<div class="sub">Goal 1,000 by Jan 31 &middot; {days_left} days left</div></div>
 <div class="tile"><div class="lab">TikTok followers</div><div class="big">{n(fol)}</div>{bar(fol, 1000)}<div class="sub">TikTok Shop opens at 1,000</div></div>
 <div class="tile"><div class="lab">Posts scheduled</div><div class="big">{len(queue)}</div><div class="sub">{('Next: ' + t(datetime.fromisoformat(queue[0]['due'].replace('Z', '+00:00')))) if queue else 'Nothing scheduled'}</div></div>
</div>
<div class="card"><h2>Views right now</h2><p class="note">From YouTube Studio and TikTok Studio. Refreshes every two hours, 8am to 10pm. Instagram isn't connected yet.</p>
<div class="scroll"><table><tr><th>Posted</th><th>Where</th><th>Post</th><th class="num">Views</th><th class="num">Likes</th><th class="num">Comments</th></tr>{post_rows}</table></div></div>
<div class="card"><h2>Coming up</h2><p class="note">Scheduled in Buffer, Central time.</p>
<div class="scroll"><table><tr><th>When</th><th>Where</th><th>Post</th></tr>{q_rows}</table></div></div>
<div class="card"><h2>Scripts and plans</h2><ul class="links">
<li><a href="https://claude.ai/artifact/B6LaKxAhra5U5DWPLukkHi">Social scripts</a><span>Every Short and reel script, plus niche alerts</span></li>
<li><a href="https://claude.ai/artifact/2fYoZeQUiPx5zDPUzJwh7W">YouTube scripts</a><span>Long-form scripts and the weekly playbook study</span></li>
<li><a href="https://claude.ai/artifact/1F6x19rtAYneTLeJSfjM8g">Monetization plan</a><span>Partner Program, TikTok Shop and Amazon goals</span></li>
<li><a href="https://github.com/philliptmckinney/mygamerfeed-posts/blob/main/QA_REEL.md">QA checklist</a><span>The rules every reel and carousel passes</span></li>
</ul></div>
<div class="card"><h2>What runs on its own</h2><ul class="auto">
<li>5:47am niche alerts<span>What's blowing up on YouTube and trending on TikTok</span></li>
<li>6:36am reel pitch<span>Today's topics and scripts</span></li>
<li>7:37am morning report<span>Live Studio numbers, with a Buffer backup at 8:07</span></li>
<li>Every 2 hours, 8am to 10pm<span>This page refreshes</span></li>
<li>9:13am, 2:13pm, 8:13pm comment sweeps<span>Drafts replies for your yes</span></li>
<li>11:38am TikTok news carousel</li>
<li>Sunday 3:23pm playbook study, 4:47pm Monday scripts</li>
</ul></div>
</div>
"""
open(out, "w").write(page)
print("ok", len(rows), "posts", len(queue), "queued")
