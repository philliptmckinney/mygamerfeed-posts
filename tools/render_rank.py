"""@mygamerfeed ranking carousel: cover, countdown tiers (lowest first, #1 last), creator pick, follow.
Usage: python3 render_rank.py rank.json outdir
rank.json: {"title":[l1,l2], "sub":..., "hook":..., "source":..., "color":[r,g,b],
            "tiers":[{"label":..., "items":[{"name","meta","score"}], "note":optional}],
            "pick":{"critics":..., "mine":..., "line":...}, "avatar_point":..., "avatar_thumbs":...}
"""
import json, os, sys
from PIL import Image, ImageDraw
from render_bright import (rubik, wrap, confetti, card, pill, topbar, swipe, place_avatar, follow,
                           INK, WHITE, YELLOW, TEXT2, SOFT)

W, H = 1080, 1350
TIER_COLORS = [(0, 190, 200), (41, 121, 255), (128, 72, 255), (255, 61, 129), (255, 122, 0), (20, 196, 110)]


def score_badge(d, x, y, score, big=False):
    r = 66 if big else 54
    col = (32, 190, 90) if score >= 90 else (255, 196, 0) if score >= 75 else (255, 90, 60)
    d.rounded_rectangle([x + 6, y + 6, x + 2 * r + 6, y + 2 * r + 6], 26, fill=INK)
    d.rounded_rectangle([x, y, x + 2 * r, y + 2 * r], 26, fill=col, outline=INK, width=5)
    d.text((x + r, y + r + 3), str(score), font=rubik(int(r * 1.05)), fill=WHITE, anchor="mm",
           stroke_width=3, stroke_fill=INK)


def cover(data, total):
    bg = tuple(data["color"])
    img = Image.new("RGB", (W, H), bg)
    confetti(img, bg, 5)
    d = ImageDraw.Draw(img)
    topbar(d, W, 1, total)
    y = 300
    d.text((60, y), data["title"][0], font=rubik(104), fill=INK)
    d.text((60, y + 110), data["title"][1], font=rubik(150), fill=WHITE, stroke_width=8, stroke_fill=INK)
    y += 300
    pill(d, 64, y, data["sub"], WHITE, rubik(38, "ExtraBold"), h=70, pad=28)
    y += 130
    hl = wrap(d, data["hook"], rubik(50, "Bold"), W - 120 - 400)
    card(d, [60, y, W - 60, y + 92 + 62 * len(hl)])
    yy = y + 46
    for line in hl:
        d.text((100, yy), line, font=rubik(50, "Bold"), fill=INK)
        yy += 62
    place_avatar(img, d, data.get("avatar_point"), (W - 400, y - 120, W - 70, y + 260))
    swipe(d, W, H)
    return img


def tier(t, i, total):
    c = TIER_COLORS[(i - 2) % len(TIER_COLORS)]
    img = Image.new("RGB", (W, H), c)
    confetti(img, c, i * 13)
    d = ImageDraw.Draw(img)
    topbar(d, W, i, total)
    items = t["items"]
    big = len(items) == 1
    row = 250 if big else 200
    ch = 120 + row * len(items) + (60 if t.get("note") else 0) + 30
    y0 = max(190, (H - ch) // 2)
    card(d, [60, y0, W - 60, y0 + ch])
    pill(d, 100, y0 + 40, t["label"], YELLOW, rubik(34), h=64, pad=26)
    y = y0 + 140
    nf = rubik(64 if big else 50)
    for it in items:
        score_badge(d, 100, y, it["score"], big)
        x = 100 + (132 if big else 108) + 36
        lines = wrap(d, it["name"], nf, W - 60 - 50 - x)
        ly = y + (10 if len(lines) > 1 else 22)
        for line in lines[:2]:
            d.text((x, ly), line, font=nf, fill=INK)
            ly += (70 if big else 56)
        d.text((x, ly + 4), it["meta"], font=rubik(32, "SemiBold"), fill=SOFT)
        y += row
    if t.get("note"):
        d.text((100, y + 4), t["note"], font=rubik(34, "Bold"), fill=TEXT2)
    d.text((64, H - 112), t.get("source", "Scores: Metacritic"), font=rubik(30, "Bold"), fill=WHITE, stroke_width=3, stroke_fill=INK)
    if i < total:
        swipe(d, W, H)
    return img


def pick(p, i, total, avatar):
    c = (255, 61, 129)
    img = Image.new("RGB", (W, H), c)
    confetti(img, c, 77)
    d = ImageDraw.Draw(img)
    topbar(d, W, i, total)
    y = 230
    d.text((60, y), "CRITICS SAY", font=rubik(64), fill=WHITE, stroke_width=5, stroke_fill=INK)
    y += 84
    card(d, [60, y, W - 60, y + 150])
    d.text((100, y + 75), p["critics"], font=rubik(56), fill=INK, anchor="lm")
    y += 210
    d.text((60, y), "MY PICK", font=rubik(64), fill=YELLOW, stroke_width=5, stroke_fill=INK)
    y += 84
    card(d, [60, y, W - 60, y + 150], fill=YELLOW)
    d.text((100, y + 75), p["mine"], font=rubik(56), fill=INK, anchor="lm")
    y += 220
    for line in wrap(d, p["line"], rubik(46, "Bold"), W - 120 - 330):
        d.text((64, y), line, font=rubik(46, "Bold"), fill=WHITE, stroke_width=3, stroke_fill=INK)
        y += 58
    place_avatar(img, d, avatar, (W - 380, H - 520, W - 50, H - 170))
    swipe(d, W, H)
    return img


def main():
    data = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    total = 1 + len(data["tiers"]) + (1 if data.get("pick") else 0) + 1
    slides = [cover(data, total)]
    for k, t in enumerate(data["tiers"]):
        slides.append(tier(t, k + 2, total))
    if data.get("pick"):
        slides.append(pick(data["pick"], len(slides) + 1, total, data.get("avatar_thumbs")))
    slides.append(follow(W, H, total, data.get("avatar_thumbs")))
    for n, s in enumerate(slides, 1):
        s.save(os.path.join(out, f"{n:02d}.jpg"), quality=92)
    print(total, "slides")


if __name__ == "__main__":
    main()
