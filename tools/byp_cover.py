import os, sys
S = "/tmp/claude-0/-home-claude/84d9a987-6211-59bf-b239-4931e378b385/scratchpad"
sys.path.insert(0, S + "/r_d10"); sys.path.insert(0, S + "/r_s1")
from h import *
from m import blur_still, P, numbadge, toggle
from PIL import Image, ImageDraw, ImageFilter
POSE = '/home/claude/mygamerfeed-posts/assets/poses/mgf_pose_%s_cutout.png'
THUMBS = "/home/claude/mascot_page/thumbs_2.png"
OUT = S + "/byp/out"; os.makedirs(OUT, exist_ok=True)
GREY = (90, 90, 100)

def fit_h(path, h):
    im = Image.open(path).convert("RGBA"); bb = im.getbbox(); im = im.crop(bb)
    return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)

def shadow_rr(d, box, r, fill, outline=INK, w=8, off=12):
    x0, y0, x1, y1 = box
    d.rounded_rectangle((x0 + off, y0 + off, x1 + off, y1 + off), r, fill=INK)
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=w)

# ---------- logo A: pill + episode tab
def logo_a(ep="02", scale=1.0):
    f = font(int(78 * scale)); f2 = font(int(46 * scale))
    tw = ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength("BEFORE YOU PLAY", font=f)
    ew = ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength("EP " + ep, font=f2)
    pw = int(tw + 90 * scale); hgt = int(140 * scale); tabw = int(ew + 60 * scale)
    im = Image.new("RGBA", (pw + tabw + 40, hgt + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    shadow_rr(d, (pw - 30, 14, pw + tabw, hgt - 4), 30, INK, w=6, off=8)
    d.text((pw + tabw / 2 - 12, hgt / 2 + 4), "EP " + ep, font=f2, fill=YELLOW, anchor="mm")
    shadow_rr(d, (0, 0, pw, hgt), hgt / 2, YELLOW, w=int(8 * scale), off=int(10 * scale))
    d.text((pw / 2, hgt / 2), "BEFORE YOU PLAY", font=f, fill=INK, anchor="mm")
    return im

# ---------- logo B: round seal with toggle
def logo_b(ep=None, size=520):
    im = Image.new("RGBA", (size + 20, size + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((14, 14, size + 14, size + 14), fill=INK)
    d.ellipse((0, 0, size, size), fill=YELLOW, outline=INK, width=12)
    d.ellipse((34, 34, size - 34, size - 34), outline=INK, width=6)
    d.text((size / 2, size * 0.27), "BEFORE", font=font(int(size * 0.13)), fill=INK, anchor="mm")
    d.text((size / 2, size * 0.75), "YOU PLAY", font=font(int(size * 0.115)), fill=INK, anchor="mm")
    t = toggle(True).resize((int(size * 0.5), int(size * 0.5 * 110 / 200)), Image.LANCZOS)
    im.alpha_composite(t, (int(size / 2 - t.width / 2), int(size / 2 - t.height / 2)))
    return im

# ---------- logo C: checklist card
def logo_c(ep=None):
    w, hgt = 820, 520
    im = Image.new("RGBA", (w + 20, hgt + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    shadow_rr(d, (0, 0, w, hgt), 44, WHITE)
    d.rounded_rectangle((0, 0, w, 150), 44, fill=INK)
    d.rectangle((0, 100, w, 150), fill=INK)
    d.text((w / 2, 78), "BEFORE YOU PLAY", font=font(76), fill=YELLOW, anchor="mm")
    for i in range(3):
        y = 200 + i * 100
        d.rounded_rectangle((60, y, 130, y + 70), 14, fill=GREEN, outline=INK, width=6)
        d.line((76, y + 36, 92, y + 54, 116, y + 18), fill=WHITE, width=10, joint="curve")
        d.rounded_rectangle((160, y + 18, 160 + (560, 470, 380)[i], y + 52), 17, fill=(225, 225, 232))
    return im

# ---------- logo D: mascot badge
def logo_d(ep=None):
    w = 900
    im = Image.new("RGBA", (w + 20, 760), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((w / 2 - 250 + 12, 22, w / 2 + 250 + 12, 522), fill=INK)
    d.ellipse((w / 2 - 250, 10, w / 2 + 250, 510), fill=YELLOW, outline=INK, width=12)
    m = fit_h(POSE % "thinking_a", 470)
    mask = Image.new("L", im.size, 0); ImageDraw.Draw(mask).ellipse((w / 2 - 238, 22, w / 2 + 238, 498), fill=255)
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0)); layer.alpha_composite(m, (int(w / 2 - m.width / 2), 60))
    layer.putalpha(Image.composite(layer.getchannel("A"), Image.new("L", im.size, 0), mask))
    im.alpha_composite(layer)
    d = ImageDraw.Draw(im)
    shadow_rr(d, (40, 470, w - 40, 610), 34, INK, outline=WHITE, w=8, off=10)
    d.text((w / 2, 540), "BEFORE YOU PLAY", font=font(84), fill=YELLOW, anchor="mm")
    return im

def board():
    c = Image.new("RGB", (2200, 1500), (32, 34, 44)); d = ImageDraw.Draw(c)
    items = [("A", "PILL + EPISODE TAB", logo_a("02")), ("B", "SETTINGS SEAL", logo_b()), ("C", "CHECKLIST CARD", logo_c()), ("D", "MASCOT BADGE", logo_d())]
    for i, (k, lab, im) in enumerate(items):
        cx = 550 + (i % 2) * 1100; cy = 380 + (i // 2) * 720
        sc = min(900 / im.width, 520 / im.height, 1.0)
        im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
        c.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)
        d.text((cx, cy + 320), f"{k}.  {lab}", font=font(44), fill=WHITE, anchor="mm")
    c.save(OUT + "/byp_logo_options.png")

# ---------- cover template
def cover(ep, l1, l2, items, bg, cred, pose_thumbs=True, logo="A"):
    c = blur_still(bg, 0.55).convert("RGBA"); d = ImageDraw.Draw(c)
    # series frame: thick yellow border so episodes read as a set on the grid
    d.rectangle((0, 0, W - 1, H - 1), outline=YELLOW, width=26)
    lg = logo_a(ep, 0.9) if logo == "A" else logo_b(size=300)
    c.alpha_composite(lg, (int(CX - lg.width / 2), 390))
    for i, (t, col, sz) in enumerate([(l1, WHITE, 112), (l2, YELLOW, 112)]):
        place(c, big_text(t, sz, col), CX, 660 + i * 130, 1, 1, rot=-2)
    # numbered list
    w = 860; rh = 112; card = Image.new("RGBA", (w + 16, 30 + rh * len(items) + 30), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
    hh = card.size[1]
    cd.rounded_rectangle((12, 16, w + 12, hh - 4), 38, fill=INK)
    cd.rounded_rectangle((0, 0, w, hh - 20), 38, fill=WHITE, outline=INK, width=8)
    for i, t in enumerate(items):
        y = 24 + i * rh
        cd.ellipse((36, y + 16, 116, y + 96), fill=YELLOW, outline=INK, width=6)
        cd.text((76, y + 57), str(i + 1), font=font(52), fill=INK, anchor="mm")
        f = font(50)
        while cd.textlength(t, font=f) > w - 190: f = font(f.size - 2)
        cd.text((146, y + 56), t, font=f, fill=INK, anchor="lm")
    c.alpha_composite(card, (int(CX - card.width / 2), 900))
    m = fit_h(THUMBS, 420)
    c.alpha_composite(m, (W - m.width - 40, 1380))
    handle(c); credit(c, cred)
    return c.convert("RGB")

if __name__ == "__main__":
    board()
    a = cover("01", "4 PS5 SETTINGS", "BEFORE GTA 6", ["VRR", "120HZ OUTPUT", "ADJUST HDR", "3D AUDIO"], P("press", "ss", "Places", "Vice City", "Vice_City_10.jpg"), "IMAGES: ROCKSTAR GAMES")
    b = cover("02", "4 SWITCH 2 SETTINGS", "FOR OCARINA", ["HDR OUTPUT", "ADJUST HDR", "VRR OUTPUT", "AUTO LOW-LATENCY MODE"], P("press", "oot", "img", "screenshot_03.jpg"), "IMAGES: NINTENDO")
    a.save(OUT + "/byp_cover_ep01_sample.png"); b.save(OUT + "/byp_cover_ep02.png")
    g = Image.new("RGB", (1080 * 3 + 40, 1440), (255, 255, 255))
    for i, im in enumerate([b, a, Image.open(S + "/cover/2026-11-20-gta6-379-billion.png").convert("RGB")]):
        g.paste(im.crop((0, 240, 1080, 1680)), (i * 1100, 0))
    g.resize((g.width // 3, g.height // 3)).save(OUT + "/byp_grid_preview.png")
    print("ok")

def checklist_card(items, w=880):
    rh = 98; head = 110
    im = Image.new("RGBA", (w + 20, head + rh * len(items) + 50), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    hh = im.size[1] - 20
    shadow_rr(d, (0, 0, w, hh), 40, WHITE)
    d.rounded_rectangle((0, 0, w, head), 40, fill=INK); d.rectangle((0, head - 40, w, head), fill=INK)
    d.rounded_rectangle((0, 0, w, hh), 40, outline=INK, width=8)
    d.text((w / 2, head / 2 + 4), "CHANGE THESE FIRST", font=font(52), fill=YELLOW, anchor="mm")
    for i, t in enumerate(items):
        y = head + 22 + i * rh
        d.rounded_rectangle((44, y + 12, 114, y + 82), 16, fill=GREEN, outline=INK, width=6)
        d.line((58, y + 48, 74, y + 64, 100, y + 30), fill=WHITE, width=10, joint="curve")
        f = font(50)
        while d.textlength(t, font=f) > w - 200: f = font(f.size - 2)
        d.text((144, y + 47), t, font=f, fill=INK, anchor="lm")
    return im

def cover2(ep, l1, l2, items, bg, cred):
    c = blur_still(bg, 0.55).convert("RGBA"); d = ImageDraw.Draw(c)
    d.rectangle((0, 0, W - 1, H - 1), outline=YELLOW, width=26)
    seal = logo_b(size=280); c.alpha_composite(seal, (int(CX - 150), 330))
    place(c, fpill("EP " + ep, 44, WHITE), CX + 190, 580, 1, 1, rot=6)
    for i, (t, col) in enumerate([(l1, WHITE), (l2, YELLOW)]):
        place(c, big_text(t, 104, col), CX, 700 + i * 115, 1, 1, rot=-2)
    card = checklist_card(items); c.alpha_composite(card, (int(CX - card.width / 2), 880))
    m = fit_h(THUMBS, 330); c.alpha_composite(m, (W - m.width - 30, 1400))
    handle(c); credit(c, cred)
    return c.convert("RGB")

if __name__ == "__main__":
    b2 = cover2("02", "4 SWITCH 2 SETTINGS", "FOR OCARINA", ["HDR OUTPUT", "ADJUST HDR", "VRR OUTPUT", "AUTO LOW-LATENCY MODE"], P("press", "oot", "img", "screenshot_03.jpg"), "IMAGES: NINTENDO")
    a2 = cover2("01", "4 PS5 SETTINGS", "BEFORE GTA 6", ["VRR", "120HZ OUTPUT", "ADJUST HDR", "3D AUDIO"], P("press", "ss", "Places", "Vice City", "Vice_City_10.jpg"), "IMAGES: ROCKSTAR GAMES")
    b2.save(OUT + "/byp_cover_v2_ep02.png"); a2.save(OUT + "/byp_cover_v2_ep01.png")
    s = Image.new("RGB", (1100, 960)); s.paste(b2.resize((540, 960)), (0, 0)); s.paste(a2.resize((540, 960)), (560, 0)); s.save(OUT + "/byp_cover_v2_pair.jpg")
