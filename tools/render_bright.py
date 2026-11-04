"""@mygamerfeed bright carousel: cover, one slide per story, follow slide.
Usage: python3 render_bright.py stories.json outdir [WxH] [avatar_point.png] [avatar_thumbs.png]
Avatars are optional transparent PNGs; without them a placeholder spot is drawn.
"""
import json, os, random, sys
from PIL import Image, ImageDraw, ImageFont

F = "/home/claude/fonts"
INK = (20, 18, 32)
TEXT2 = (70, 68, 88)
SOFT = (130, 128, 150)
WHITE = (255, 255, 255)
CAT = {"INDUSTRY": (255, 61, 129), "HARDWARE": (41, 121, 255), "PC": (128, 72, 255),
       "CONSOLE": (20, 196, 110), "HANDHELD": (0, 190, 200), "MOBILE": (0, 190, 200),
       "AI": (255, 196, 0), "LEGAL": (255, 122, 0), "RELEASE": (0, 186, 230)}
STATUS = {"CONFIRMED": (32, 210, 120), "REPORTED": (60, 160, 255), "UNCONFIRMED": (255, 150, 0)}
YELLOW = (255, 214, 0)


def rubik(size, weight="Black"):
    f = ImageFont.truetype(f"{F}/Rubik.ttf", size)
    f.set_variation_by_name(weight)
    return f


def wrap(d, text, font, max_w):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def tint(c, amt):
    return tuple(int(v + (255 - v) * amt) for v in c)


def confetti(img, color, seed):
    """Background of generic controller button prompts: face buttons, shape buttons, triggers, d-pad."""
    W, H = img.size
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    rnd = random.Random(seed)
    light = tint(color, 0.38) + (170,)
    kinds = ["A", "B", "X", "Y", "o", "x", "t", "s", "ZR", "RB", "L2", "dpad"]
    cells = [(cx, cy) for cx in range(0, W, 270) for cy in range(0, H, 270)]
    rnd.shuffle(cells)
    for cx, cy in cells[:14]:
        x, y = cx + rnd.randint(20, 150), cy + rnd.randint(20, 150)
        s = rnd.randint(58, 88)
        k = rnd.choice(kinds)
        if k in ("A", "B", "X", "Y"):
            d.ellipse([x, y, x + s, y + s], outline=light, width=9)
            d.text((x + s / 2, y + s / 2 + 2), k, font=rubik(int(s * .52)), fill=light, anchor="mm")
        elif k == "o":
            d.ellipse([x, y, x + s, y + s], outline=light, width=10)
        elif k == "x":
            d.line([(x, y), (x + s, y + s)], fill=light, width=12)
            d.line([(x + s, y), (x, y + s)], fill=light, width=12)
        elif k == "t":
            d.polygon([(x, y + s), (x + s / 2, y), (x + s, y + s)], outline=light, width=10)
        elif k == "s":
            d.rectangle([x, y, x + s, y + s], outline=light, width=10)
        elif k == "dpad":
            t = s * .34
            d.rounded_rectangle([x + t, y, x + s - t, y + s], 8, outline=light, width=8)
            d.rounded_rectangle([x, y + t, x + s, y + s - t], 8, outline=light, width=8)
        else:
            w = s * 1.5
            d.rounded_rectangle([x, y, x + w, y + s * .7], int(s * .3), outline=light, width=8)
            d.text((x + w / 2, y + s * .35 + 2), k, font=rubik(int(s * .38)), fill=light, anchor="mm")
    img.paste(lay, (0, 0), lay)


def abtn(d, x, y, r, fill=INK, fg=WHITE, letter="A"):
    d.ellipse([x, y, x + 2 * r, y + 2 * r], fill=fill)
    d.text((x + r, y + r + 2), letter, font=rubik(int(r * 1.1)), fill=fg, anchor="mm")


def card(d, box, r=44, shadow=14, fill=WHITE):
    x0, y0, x1, y1 = box
    d.rounded_rectangle([x0 + shadow, y0 + shadow, x1 + shadow, y1 + shadow], r, fill=INK)
    d.rounded_rectangle(box, r, fill=fill, outline=INK, width=6)


def pill(d, x, y, label, fill, font, fg=INK, pad=22, h=56):
    tw = d.textlength(label, font=font)
    d.rounded_rectangle([x, y, x + tw + pad * 2, y + h], h // 2, fill=fill, outline=INK, width=4)
    d.text((x + pad, y + h / 2), label, font=font, fill=fg, anchor="lm")
    return x + tw + pad * 2


def topbar(d, W, idx, total):
    pill(d, 60, 60, "@mygamerfeed", WHITE, rubik(32), h=66)
    if not total:
        return
    c = f"{idx}/{total}"
    f = rubik(28, "Bold")
    tw = d.textlength(c, font=f)
    pill(d, W - 60 - tw - 44, 64, c, WHITE, f, h=58)


def swipe(d, W, H):
    f = rubik(32)
    t = "NEXT"
    tw = d.textlength(t, font=f)
    w, h = tw + 120, 76
    x, y = W - 60 - w, H - 136
    d.rounded_rectangle([x + 8, y + 8, x + w + 8, y + h + 8], h // 2, fill=INK)
    d.rounded_rectangle([x, y, x + w, y + h], h // 2, fill=YELLOW, outline=INK, width=4)
    abtn(d, x + 12, y + 12, 26)
    d.text((x + 82, y + h / 2), t, font=f, fill=INK, anchor="lm")


def place_avatar(img, d, avatar, box):
    x0, y0, x1, y1 = box
    if avatar and os.path.exists(avatar):
        a = Image.open(avatar).convert("RGBA")
        a.thumbnail((x1 - x0, y1 - y0), Image.NEAREST if (a.width % 14 == 0 and a.height % 14 == 0) else Image.LANCZOS)
        img.paste(a, (x1 - a.width, y1 - a.height), a)
    else:
        d.rounded_rectangle(box, 40, outline=INK, width=5, fill=tint(YELLOW, 0.5))
        d.text(((x0 + x1) / 2, (y0 + y1) / 2), "AVATAR", font=rubik(34), fill=INK, anchor="mm")


COVERS = [(255, 214, 0), (255, 61, 129), (41, 121, 255), (20, 196, 110), (255, 122, 0), (0, 190, 200)]


def cover_color():
    from datetime import datetime
    from zoneinfo import ZoneInfo
    now = datetime.now(ZoneInfo("America/Chicago"))
    slot = min(range(4), key=lambda k: abs(now.hour - (7, 11, 15, 19)[k]))
    return COVERS[(now.toordinal() * 4 + slot) % len(COVERS)]


def cover(data, W, H, total, avatar, story_mode=False):
    bg = tuple(data.get("cover_color") or cover_color())
    img = Image.new("RGB", (W, H), bg)
    confetti(img, (255, 160, 0) if bg == YELLOW else bg, 3)
    d = ImageDraw.Draw(img)
    topbar(d, W, 1, total)
    y = 190 if H < 1600 else 320
    d.text((64, y), data["date"], font=rubik(36, "ExtraBold"), fill=INK)
    y += 50
    d.text((60, y), "TODAY IN", font=rubik(96), fill=INK)
    d.text((60, y + 92), "GAMING", font=rubik(150), fill=WHITE, stroke_width=8, stroke_fill=INK)
    y += 290
    rows = data["stories"]
    f = rubik(40, "Bold")
    inner_w = W - 120 - 130
    heights = [len(wrap(d, s["short"], f, inner_w)) * 50 + (40 if s["status"] == "UNCONFIRMED" else 0) for s in rows]
    ch = sum(heights) + 34 * (len(rows) - 1) + 80
    card(d, [60, y, W - 60, y + ch])
    yy = y + 40
    for s, h in zip(rows, heights):
        c = CAT.get(s["tag"], (128, 72, 255))
        d.ellipse([96, yy - 2, 150, yy + 52], fill=c, outline=INK, width=4)
        d.text((123, yy + 25), str(rows.index(s) + 1), font=rubik(30), fill=WHITE, anchor="mm")
        ly = yy
        for line in wrap(d, s["short"], f, inner_w):
            d.text((180, ly), line, font=f, fill=INK)
            ly += 50
        if s["status"] == "UNCONFIRMED":
            d.text((180, ly + 2), "UNCONFIRMED", font=rubik(26, "ExtraBold"), fill=STATUS["UNCONFIRMED"])
        yy += h + 34
    top = 170 if H < 1600 else 300
    place_avatar(img, d, avatar, (W - 360, top, W - 50, top + 330))
    if story_mode:
        f = rubik(40)
        t = "NEW POST ON OUR PAGE"
        tw = d.textlength(t, font=f)
        w, h = tw + 150, 100
        x, y = (W - w) // 2, yy + 60
        d.rounded_rectangle([x + 10, y + 10, x + w + 10, y + h + 10], h // 2, fill=INK)
        d.rounded_rectangle([x, y, x + w, y + h], h // 2, fill=WHITE, outline=INK, width=4)
        abtn(d, x + 16, y + 16, 34)
        d.text((x + 100, y + h / 2), t, font=f, fill=INK, anchor="lm")
    return img


def story(s, i, W, H, total):
    c = CAT.get(s["tag"], (128, 72, 255))
    img = Image.new("RGB", (W, H), c)
    confetti(img, c, i * 11)
    d = ImageDraw.Draw(img)
    topbar(d, W, i, total)
    M, P = 60, 56
    maxw = W - 2 * M - 2 * P
    hf, bf = rubik(76), rubik(40, "Medium")
    hl, bl = wrap(d, s["head"], hf, maxw), wrap(d, s["body"], bf, maxw)
    ch = P + 56 + 44 + len(hl) * 84 + 30 + len(bl) * 54 + 36 + 34 + P
    y0 = max(180, (H - ch) // 2 - 10)
    card(d, [M, y0, W - M, y0 + ch])
    x, y = M + P, y0 + P
    sf = rubik(28)
    nx = pill(d, x, y, s["tag"], c, sf, fg=WHITE if s["tag"] not in ("AI", "LEGAL") else INK)
    pill(d, nx + 14, y, s["status"], STATUS[s["status"]], sf, fg=INK)
    y += 56 + 44
    for line in hl:
        d.text((x, y), line, font=hf, fill=INK)
        y += 84
    y += 30
    for line in bl:
        d.text((x, y), line, font=bf, fill=TEXT2)
        y += 54
    y += 36
    d.text((x, y), "Source: " + s["source"], font=rubik(28, "SemiBold"), fill=SOFT)
    if i < total:
        swipe(d, W, H)
    return img


def follow(W, H, total, avatar):
    c = (128, 72, 255)
    img = Image.new("RGB", (W, H), c)
    confetti(img, c, 99)
    d = ImageDraw.Draw(img)
    topbar(d, W, total, total)
    y = 240 if H < 1600 else 420
    for line in ["STAY IN", "THE LOOP."]:
        d.text((60, y), line, font=rubik(118), fill=WHITE, stroke_width=7, stroke_fill=INK)
        y += 124
    y += 20
    for line in ["Gaming news, one swipe at a time."]:
        d.text((64, y), line, font=rubik(42, "Bold"), fill=WHITE)
        y += 54
    y += 50
    f = rubik(40)
    t = "FOLLOW @mygamerfeed"
    tw = d.textlength(t, font=f)
    w, h = tw + 150, 100
    d.rounded_rectangle([70, y + 10, 70 + w, y + h + 10], h // 2, fill=INK)
    d.rounded_rectangle([60, y, 60 + w, y + h], h // 2, fill=YELLOW, outline=INK, width=4)
    abtn(d, 76, y + 16, 34)
    d.text((160, y + h / 2), t, font=f, fill=INK, anchor="lm")
    abox = (W - 420, H - 520, W - 40, H - 40) if H < 1600 else (W - 480, H - 640, W - 40, H - 120)
    place_avatar(img, d, avatar, abox)
    return img


def main():
    data = json.load(open(sys.argv[1]))
    out = sys.argv[2]
    W, H = (map(int, sys.argv[3].split("x")) if len(sys.argv) > 3 and sys.argv[3] not in ("-", "story") else (1080, 1350))
    av1 = sys.argv[4] if len(sys.argv) > 4 else None
    av2 = sys.argv[5] if len(sys.argv) > 5 else None
    os.makedirs(out, exist_ok=True)
    if len(sys.argv) > 3 and sys.argv[3] == "story":
        cover(data, 1080, 1920, 0, av1, story_mode=True).save(f"{out}/story.png")
        print(f"story -> {out}/story.png")
        return
    total = len(data["stories"]) + 2
    slides = [cover(data, W, H, total, av1)]
    slides += [story(s, i + 2, W, H, total) for i, s in enumerate(data["stories"])]
    slides.append(follow(W, H, total, av2))
    for n, im in enumerate(slides, 1):
        im.save(f"{out}/slide_{n:02d}.png")
    print(f"{len(slides)} slides -> {out}")


if __name__ == "__main__":
    main()
