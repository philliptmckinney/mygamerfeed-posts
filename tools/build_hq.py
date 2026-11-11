"""Build the Gamer Feed HQ page. The stats are plain HTML and CSS; the Inbox at the top is live from the
page's db (collection "inbox"), which every @mygamerfeed scheduled task writes to (see INBOX.md).
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
.inbox h2 {{ display:-webkit-box; display:flex; -webkit-box-align:center; align-items:center; }}
.count {{ margin-left:8px; font-size:12px; font-weight:700; background:var(--accent); color:#fff; border-radius:999px; padding:1px 8px; }}
.item {{ border-top:1px solid var(--line); padding:10px 0; }}
.item:first-of-type {{ border-top:0; }}
.src {{ font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:.06em; color:var(--muted); }}
.alert .src {{ color:var(--yt); }}
.ttl {{ font-weight:600; margin:2px 0; }}
.body {{ white-space:pre-wrap; font-size:13px; color:var(--fg); margin:4px 0; }}
.when {{ font-size:12px; color:var(--muted); }}
.btns {{ margin-top:6px; }}
button {{ font:inherit; font-size:13px; font-weight:600; border-radius:8px; border:1px solid var(--line); background:var(--panel); color:var(--fg); padding:6px 12px; margin:0 6px 6px 0; cursor:pointer; }}
button.go {{ background:var(--accent); border-color:var(--accent); color:#fff; }}
button:disabled {{ opacity:.5; }}
.c {{ border:1px solid var(--line); border-radius:10px; padding:10px; margin:8px 0; }}
.c .q {{ font-size:13px; color:var(--muted); margin:2px 0 6px; }}
textarea {{ width:100%; box-sizing:border-box; font:inherit; font-size:14px; border:1px solid var(--line); border-radius:8px; background:var(--bg); color:var(--fg); padding:8px; min-height:56px; }}
.st {{ font-size:12px; font-weight:700; }}
.st.approved, .st.posted {{ color:var(--good); }} .st.skipped {{ color:var(--muted); }}
details summary {{ cursor:pointer; color:var(--accent); font-size:13px; font-weight:600; margin-top:4px; }}
.empty {{ color:var(--muted); font-size:13px; }}
</style>
<div class="wrap">
<h1>Gamer Feed HQ</h1>
<p class="lede">Updated {t(up)} Central. <b>{n(yt_week)}</b> YouTube views and <b>{n(tt_week)}</b> TikTok views on posts from the last 7 days. {best_line}</p>
<div class="card inbox" id="needs"><h2>Needs you <span class="count" id="ncount" style="display:none"></span></h2><p class="note">Comment replies to approve, voiceovers to review, and anything that failed. Approved replies post on the next comment sweep.</p><div id="needs-list"><p class="empty">Open this page in the Claude app to load your inbox.</p></div></div>
<div class="card inbox"><h2>Latest updates</h2><p class="note">What each task did, newest first. Nothing here needs you.</p><div id="info-list"><p class="empty">Loading.</p></div></div>
<div class="tiles">
 <div class="tile"><div class="lab">YouTube subscribers</div><div class="big">{n(subs)}</div>{bar(subs, 1000)}<div class="sub">Goal 1,000 by Jan 31 &middot; {days_left} days left</div></div>
 <div class="tile"><div class="lab">TikTok followers</div><div class="big">{n(fol)}</div>{bar(fol, 1000)}<div class="sub">TikTok Shop opens at 1,000</div></div>
 <div class="tile"><div class="lab">Posts scheduled</div><div class="big">{len(queue)}</div><div class="sub">{('Next: ' + t(datetime.fromisoformat(queue[0]['due'].replace('Z', '+00:00')))) if queue else 'Nothing scheduled'}</div></div>
</div>
<div class="card"><h2>Views right now</h2><p class="note">From YouTube Studio and TikTok Studio. Refreshes at 8am and 7pm. Instagram isn't connected yet.</p>
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
<li>7:37am morning report<span>Live numbers, plus a fact check on today's posts before they go out</span></li>
<li>9:13am, 2:13pm, 8:13pm comment sweeps<span>Drafts replies here for your approval, and posts the ones you approved</span></li>
<li>11:38am TikTok news carousel</li>
<li>11:52am, 12:52pm, 3:52pm, 6:52pm post check<span>Confirms posts went live and tops up the Buffer queue</span></li>
<li>8:07am and 7:07pm<span>This page's numbers refresh</span></li>
<li>Sunday 3:23pm playbook study, 4:47pm weekly scripts, 9:37pm audio cleanup</li>
</ul></div>
</div>
<script>
(function () {{
  var C = window.claude; if (!C || !C.use) return;
  function el(t, cls, txt) {{ var e = document.createElement(t); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }}
  function when(iso) {{ try {{ var d = new Date(iso); return d.toLocaleString([], {{weekday:'short', month:'short', day:'numeric', hour:'numeric', minute:'2-digit'}}); }} catch (e) {{ return ''; }} }}
  var needs = document.getElementById('needs-list'), info = document.getElementById('info-list'), cnt = document.getElementById('ncount');
  var timer = setTimeout(function () {{ needs.innerHTML = '<p class="empty">The inbox can’t be reached right now. The numbers below still work.</p>'; info.innerHTML = ''; }}, 10000);
  C.use('db').then(function (db) {{
    if (!db) {{ clearTimeout(timer); needs.innerHTML = '<p class="empty">Open this page in the Claude app to load your inbox.</p>'; info.innerHTML = ''; return; }}
    var busy = {{}};
    function save(ref, data, btns) {{
      if (busy[ref.path]) return; busy[ref.path] = true; btns.forEach(function (b) {{ b.disabled = true; }});
      ref.update(data).catch(function () {{ alert('That did not save. Try again in a moment.'); }}).then(function () {{ busy[ref.path] = false; btns.forEach(function (b) {{ b.disabled = false; }}); }});
    }}
    function commentsItem(d, ref, box) {{
      var items = (d.items || []).slice();
      items.forEach(function (it, i) {{
        var c = el('div', 'c');
        c.appendChild(el('div', 'src', (it.platform || '') + (it.post ? ' · ' + it.post : '')));
        c.appendChild(el('div', 'q', (it.user ? it.user + ': ' : '') + '“' + (it.comment || '') + '”'));
        if (it.status === 'pending' || !it.status) {{
          var ta = el('textarea'); ta.value = it.draft || ''; c.appendChild(ta);
          var b = el('div', 'btns'), ok = el('button', 'go', 'Approve'), no = el('button', '', 'Skip');
          function set(st) {{ var next = items.map(function (x, j) {{ if (j !== i) return x; var y = {{}}; for (var k in x) y[k] = x[k]; y.status = st; if (st === 'approved') y.draft = ta.value.trim(); return y; }}); save(ref, {{items: next}}, [ok, no]); }}
          ok.onclick = function () {{ set('approved'); }}; no.onclick = function () {{ set('skipped'); }};
          b.appendChild(ok); b.appendChild(no); c.appendChild(b);
        }} else {{
          c.appendChild(el('div', 'body', it.draft || ''));
          c.appendChild(el('div', 'st ' + it.status, it.status === 'approved' ? 'Approved, posts on the next sweep' : it.status === 'posted' ? 'Posted' : 'Skipped'));
        }}
        box.appendChild(c);
      }});
    }}
    db.collection('inbox').orderBy('created', 'desc').limit(60).onSnapshot(function (snap) {{
      if (!snap.metadata.fromCache) clearTimeout(timer);
      needs.innerHTML = ''; info.innerHTML = '';
      var n = 0, cutoff = Date.now() - 3 * 864e5;
      snap.docs.forEach(function (doc) {{
        var d = doc.data() || {{}}, ref = db.collection('inbox').doc(doc.id);
        var isComments = d.kind === 'comments';
        var open = isComments ? (d.items || []).some(function (x) {{ return !x.status || x.status === 'pending'; }}) : (d.kind === 'action' || d.kind === 'alert') && !d.done;
        if (!open && (!d.created || new Date(d.created).getTime() < cutoff)) return;
        var box = el('div', 'item' + (d.kind === 'alert' ? ' alert' : ''));
        box.appendChild(el('div', 'src', d.source || 'Update'));
        box.appendChild(el('div', 'ttl', d.title || ''));
        if (open && !isComments) {{ if (d.body) box.appendChild(el('div', 'body', d.body)); }}
        else if (d.body) {{ var det = el('details'); det.appendChild(el('summary', '', 'Details')); det.appendChild(el('div', 'body', d.body)); box.appendChild(det); }}
        if (isComments) commentsItem(d, ref, box);
        if (d.link) {{ var a = el('a', '', 'Open'); a.href = d.link; a.style.cssText = 'font-size:13px;font-weight:600;color:var(--accent)'; box.appendChild(a); }}
        box.appendChild(el('div', 'when', when(d.created)));
        if (open && !isComments) {{ var b = el('div', 'btns'), done = el('button', '', 'Mark done'); done.onclick = function () {{ save(ref, {{done: true}}, [done]); }}; b.appendChild(done); box.appendChild(b); }}
        if (open) {{ n++; needs.appendChild(box); }} else info.appendChild(box);
      }});
      if (!n) needs.innerHTML = '<p class="empty">Nothing needs you right now.</p>';
      if (!info.children.length) info.innerHTML = '<p class="empty">No updates in the last 3 days.</p>';
      cnt.style.display = n ? '' : 'none'; cnt.textContent = n;
    }}, function () {{ clearTimeout(timer); needs.innerHTML = '<p class="empty">The inbox couldn’t load. The numbers below still work.</p>'; }});
  }});
}})();
</script>
"""
open(out, "w").write(page)
print("ok", len(rows), "posts", len(queue), "queued")
