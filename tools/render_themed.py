"""Game-themed carousels: official game art full-bleed, the game's look leads, @mygamerfeed is a small accent.
Usage: python3 render_themed.py spec.json outdir
spec: {"theme":"zelda"|"gta", "kind":"rank"|"check", "slides":[...], "handle_avatar": thumbs png (follow slide only)}
Slide types:
 {"type":"cover","bg":path,"kicker":..,"title":[l1,l2],"sub":..}
 {"type":"rank","bg":path,"label":..,"items":[{"name","meta","score"}],"note":..,"source":..}
 {"type":"step","bg":path,"n":1,"head":..,"body":..,"source":..}
 {"type":"pick","bg":path,"critics":..,"mine":..,"line":..}
 {"type":"follow","bg":path,"line":..}
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1350
F = "/home/claude/fonts"
THEMES = {
    "zelda": {"accent": (232, 195, 90), "accent2": (120, 200, 120), "panel": (10, 22, 16, 205), "line": (232, 195, 90),
              "head": ("Cinzel.ttf", "Black"), "body": ("Rubik.ttf", "Medium"), "ink": (14, 20, 14)},
    "gta": {"accent": (255, 92, 160), "accent2": (255, 170, 60), "panel": (16, 10, 28, 200), "line": (255, 92, 160),
            "head": ("Anton.ttf", None), "body": ("Rubik.ttf", "Medium"), "ink": (20, 10, 30)},
}
WHITE = (255, 255, 255)


def font(spec, size):
    f = ImageFont.truetype(os.path.join(F, spec[0]), size)
    if spec[1]:
        try:
            f.set_variation_by_name(spec[1])
        except Exception:
            pass
    return f


def rub(size, w="Bold"):
    return font(("Rubik.ttf", w), size)


def wrap(d, text, f, maxw):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            out.append(cur); cur = w
    if cur:
        out.append(cur)
    return out


def bg(path, dark=0.55):
    im = Image.open(path).convert("RGB")
    s = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    im = im.crop((x, y, x + W, y + H)).convert("RGBA")
    g = Image.new("L", (1, H))
    for yy in range(H):
        t = yy / H
        g.putpixel((0, yy), int(255 * min(1, dark * (0.55 + 0.9 * abs(t - 0.45)))))
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 255)); shade.putalpha(g.resize((W, H)))
    im.alpha_composite(shade)
    return im


def handle(img):
    d = ImageDraw.Draw(img)
    f = rub(30, "ExtraBold")
    t = "@mygamerfeed"
    tw = d.textlength(t, font=f)
    x, y, h = 60, 60, 56
    d.rounded_rectangle([x, y, x + tw + 44, y + h], h // 2, fill=(255, 255, 255, 235))
    d.text((x + 22, y + h / 2), t, font=f, fill=(20, 18, 32), anchor="lm")


def panel(img, box, th):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle(box, 28, fill=th["panel"], outline=th["line"] + (255,), width=4)
    img.alpha_composite(lay)


def shadow_text(img, xy, text, f, fill, anchor="la", stroke=0):
    d = ImageDraw.Draw(img)
    x, y = xy
    d.text((x + 4, y + 5), text, font=f, fill=(0, 0, 0, 170), anchor=anchor)
    d.text((x, y), text, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))


def source(img, text):
    if text:
        shadow_text(img, (64, 1140), text, rub(28, "Bold"), (235, 235, 235))


def next_tag(img, th):
    d = ImageDraw.Draw(img)
    f = rub(30, "ExtraBold"); t = "SWIPE"
    tw = d.textlength(t, font=f)
    x, y = W - 140 - tw - 60, 1128
    d.rounded_rectangle([x, y, x + tw + 60, y + 58], 29, fill=th["accent"])
    d.text((x + 30, y + 29), t, font=f, fill=th["ink"], anchor="lm")


def cover(s, th):
    img = bg(s["bg"], 0.6)
    handle(img)
    hf = font(th["head"], 150 if th is THEMES["gta"] else 118)
    y = 560
    shadow_text(img, (64, y), s["kicker"], rub(40, "ExtraBold"), th["accent"])
    y += 70
    for i, line in enumerate(s["title"]):
        shadow_text(img, (60, y), line, hf, WHITE if i == 0 else th["accent"], stroke=3)
        y += int(hf.size * (1.02 if th is THEMES["gta"] else 1.12))
    d = ImageDraw.Draw(img)
    y += 30
    for line in wrap(d, s["sub"], rub(42, "Bold"), W - 120 - 140):
        y += 6
        shadow_text(img, (64, y + 10), line, rub(42, "Bold"), WHITE)
        y += 54
    next_tag(img, th)
    return img


def badge(img, x, y, score, th, big=False):
    d = ImageDraw.Draw(img)
    s = 124 if big else 100
    d.rounded_rectangle([x, y, x + s, y + s], 22, fill=th["accent"], outline=(0, 0, 0), width=4)
    d.text((x + s / 2, y + s / 2 + 2), str(score), font=rub(int(s * 0.5), "Black"), fill=th["ink"], anchor="mm")


def rank(s, th):
    img = bg(s["bg"], 0.62)
    handle(img)
    items = s["items"]; big = len(items) == 1
    row = 220 if big else (150 if len(items) >= 4 else 170)
    hf = font(th["head"], 72)
    top = 330 if len(items) >= 4 else 400
    shadow_text(img, (64, top), s["label"], hf, th["accent"], stroke=2)
    y0 = top + 110
    ph = 40 + row * len(items) + (70 if s.get("note") else 0)
    panel(img, [60, y0, W - 140, y0 + ph], th)
    d = ImageDraw.Draw(img)
    y = y0 + 36
    nf = rub(58 if big else 46, "ExtraBold")
    for it in items:
        badge(img, 96, y, it["score"], th, big)
        x = 96 + (124 if big else 100) + 30
        lines = wrap(d, it["name"], nf, W - 140 - 40 - x)
        ly = y + (4 if len(lines) > 1 else 14)
        for line in lines[:2]:
            d.text((x, ly), line, font=nf, fill=WHITE); ly += nf.size + 6
        d.text((x, ly + 2), it["meta"], font=rub(30, "SemiBold"), fill=(205, 205, 205))
        y += row
    if s.get("note"):
        d.text((96, y + 4), s["note"], font=rub(32, "Bold"), fill=th["accent"])
    source(img, s.get("source"))
    next_tag(img, th)
    return img


def step(s, th):
    img = bg(s["bg"], 0.6)
    handle(img)
    d = ImageDraw.Draw(img)
    nf = font(th["head"], 200)
    shadow_text(img, (60, 360), f"0{s['n']}" if s["n"] < 10 else str(s["n"]), nf, th["accent"], stroke=3)
    hf = font(th["head"], 84)
    y = 620
    for line in wrap(d, s["head"].upper() if th is THEMES["gta"] else s["head"], hf, W - 120 - 140):
        shadow_text(img, (62, y), line, hf, WHITE, stroke=2); y += int(hf.size * 1.08)
    y += 24
    bf = rub(40, "Medium")
    bl = wrap(d, s["body"], bf, W - 120 - 140 - 60)
    panel(img, [60, y, W - 140, y + 52 * len(bl) + 50], th)
    yy = y + 26
    for line in bl:
        d.text((90, yy), line, font=bf, fill=WHITE); yy += 52
    source(img, s.get("source"))
    next_tag(img, th)
    return img


def pick(s, th):
    img = bg(s["bg"], 0.62)
    handle(img)
    d = ImageDraw.Draw(img)
    hf = font(th["head"], 60)
    vf = rub(56, "ExtraBold")
    y = 420
    shadow_text(img, (64, y), "CRITICS SAY", hf, WHITE, stroke=2); y += 90
    panel(img, [60, y, W - 140, y + 120], th)
    d.text((96, y + 60), s["critics"], font=vf, fill=WHITE, anchor="lm"); y += 180
    shadow_text(img, (64, y), "MY PICK", hf, th["accent"], stroke=2); y += 90
    d.rounded_rectangle([60, y, W - 140, y + 120], 28, fill=th["accent"], outline=(0, 0, 0), width=4)
    d.text((96, y + 60), s["mine"], font=vf, fill=th["ink"], anchor="lm"); y += 170
    for line in wrap(d, s["line"], rub(44, "Bold"), W - 120 - 140):
        shadow_text(img, (64, y), line, rub(44, "Bold"), WHITE); y += 56
    next_tag(img, th)
    return img


def follow(s, th, avatar):
    img = bg(s["bg"], 0.66)
    handle(img)
    d = ImageDraw.Draw(img)
    hf = font(th["head"], 96)
    y = 470
    for line in s.get("title", ["FOLLOW FOR", "MORE"]):
        shadow_text(img, (60, y), line, hf, WHITE, stroke=2); y += int(hf.size * 1.1)
    y += 10
    for line in wrap(d, s["line"], rub(42, "Bold"), W - 120 - 380):
        shadow_text(img, (64, y), line, rub(42, "Bold"), th["accent"]); y += 54
    y += 30
    f = rub(42, "ExtraBold"); t = "@mygamerfeed"
    tw = d.textlength(t, font=f)
    d.rounded_rectangle([60, y, 60 + tw + 64, y + 84], 42, fill=th["accent"], outline=(0, 0, 0), width=4)
    d.text((92, y + 42), t, font=f, fill=th["ink"], anchor="lm")
    if avatar and os.path.exists(avatar):
        a = Image.open(avatar).convert("RGBA"); a.thumbnail((320, 340))
        img.alpha_composite(a, (W - 140 - a.width, 1080 - a.height))
    return img


def main():
    spec = json.load(open(sys.argv[1])); out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    th = THEMES[spec["theme"]]
    fns = {"cover": cover, "rank": rank, "step": step, "pick": pick}
    for i, s in enumerate(spec["slides"], 1):
        img = follow(s, th, spec.get("handle_avatar")) if s["type"] == "follow" else fns[s["type"]](s, th)
        img.convert("RGB").save(os.path.join(out, f"{i:02d}.jpg"), quality=92)
    print(len(spec["slides"]), "slides")


if __name__ == "__main__":
    main()
