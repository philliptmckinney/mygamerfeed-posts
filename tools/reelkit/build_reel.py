"""@mygamerfeed voiced reel builder (house style: glow background, top bar, Rubik Black text, pills, stickers,
pop-in animation, merch card, combined question + follow end card, 0.2 s cover frame).

Usage: python3 build_reel.py spec.json out.mp4
Spec keys:
  vo: path to the approved voiceover wav (voice is used untouched)
  music: path to the music track; music_offset: seconds into the track to start
  tag: yellow topic pill in the top bar
  cover: {"l1","l2","stamp","stamp_color","pose"}
  scenes: [{"t0","t1","kind":"text"|"merch"|"end", "items":[...]}]
     text item: {"t","type":"white|yellow|pill|sticker|num|check|icon","text","y","size","color","angle","icon"}
     end scene: {"question":[l1,l2],"next":"...","follow":[l1,l2],"extra":{"t","text"}}
  tail: seconds after the voice ends (music rises, then fades)
Assets are read from ASSETS (repo assets folder). Fonts from FONTS.
"""
import json, math, os, subprocess, sys, re
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.environ.get("MGF_ASSETS", os.path.join(HERE, "..", "assets"))
FONTS = os.environ.get("MGF_FONTS", os.path.join(HERE, "fonts"))
W, H, FPS, SR = 1080, 1920, 30, 48000
NAVY = (22, 17, 42); YEL = (255, 210, 31); PINK = (255, 79, 160); CYAN = (62, 230, 255)
GREEN = (40, 200, 110); RED = (235, 55, 70); WHITE = (255, 255, 255); BLACK = (12, 10, 20)
COLORS = {"yellow": YEL, "pink": PINK, "green": GREEN, "red": RED, "white": WHITE, "cyan": CYAN}


def F(size, name="rubik"):
    # House font is Rubik Black (900), matched to reels through Nov 25.
    files = {"rubik": "rubik-latin-900-normal.woff", "lilita": "lilita-one-latin-400-normal.woff"}
    return ImageFont.truetype(os.path.join(FONTS, files[name]), size)


def trim(im):
    bb = im.getbbox()
    return im.crop(bb) if bb else im


def outlined_text(text, size, fill, stroke=9, shadow=True, maxw=860):
    f = F(size)
    while ImageDraw.Draw(Image.new("RGBA", (1, 1))).textlength(text, font=f) + 2 * stroke > maxw and size > 30:
        size -= 2; f = F(size)
    d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bb = d0.textbbox((0, 0), text, font=f, stroke_width=stroke)
    w, h = bb[2] - bb[0] + 40, bb[3] - bb[1] + 50
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((20 - bb[0], 30 - bb[1]), text, font=f, fill=(0, 0, 0, 170), stroke_width=stroke, stroke_fill=(0, 0, 0, 170))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)))
    ImageDraw.Draw(im).text((20 - bb[0], 20 - bb[1]), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=BLACK)
    return trim(im)


def pill(text, size, bg=WHITE, fg=BLACK, outline=BLACK, pad=(26, 12), radius=None, maxw=860):
    f = F(size)
    while ImageDraw.Draw(Image.new("RGBA", (1, 1))).textlength(text, font=f) + 2 * pad[0] + 20 > maxw and size > 24:
        size -= 2; f = F(size)
    d0 = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bb = d0.textbbox((0, 0), text, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    w, h = tw + 2 * pad[0] + 12, th + 2 * pad[1] + 18
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    r = radius if radius is not None else (h - 12) // 2
    d.rounded_rectangle((6, 10, w - 1, h - 1), r, fill=(0, 0, 0, 200))
    d.rounded_rectangle((0, 0, w - 7, h - 11), r, fill=bg, outline=outline, width=5)
    d.text(((w - 7) / 2, (h - 11) / 2 + 1), text, font=f, fill=fg, anchor="mm")
    return im


def sticker(text, size, color, angle=-4):
    fg = BLACK if color in (YEL, WHITE, CYAN) else WHITE
    im = pill(text, size, bg=color, fg=fg, outline=WHITE, pad=(28, 14), radius=14)
    return im.rotate(angle, resample=Image.BICUBIC, expand=True)


def num_badge(n, size=150):
    im = Image.new("RGBA", (size + 14, size + 14), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse((8, 10, size + 12, size + 12), fill=(0, 0, 0, 200))
    d.ellipse((0, 0, size, size), fill=YEL, outline=BLACK, width=7)
    d.text((size / 2, size / 2 + 4), str(n), font=F(int(size * 0.62)), fill=BLACK, anchor="mm")
    return im


def check_row(text, size=56, ok=True):
    t = outlined_text(text, size, WHITE, stroke=7, maxw=700)
    s = t.height
    tog = Image.new("RGBA", (int(s * 1.7), s), (0, 0, 0, 0)); d = ImageDraw.Draw(tog)
    d.rounded_rectangle((0, s * 0.12, s * 1.7 - 1, s * 0.88), s * 0.38, fill=GREEN if ok else RED, outline=BLACK, width=5)
    cx = s * 1.7 - s * 0.45 if ok else s * 0.45
    d.ellipse((cx - s * 0.3, s * 0.2, cx + s * 0.3, s * 0.8), fill=WHITE, outline=BLACK, width=4)
    im = Image.new("RGBA", (tog.width + 24 + t.width, s), (0, 0, 0, 0))
    im.alpha_composite(tog, (0, 0)); im.alpha_composite(t, (tog.width + 24, 0))
    return im


# ---------- drawn icons (original art, no product photos) ----------

def icon_tv(phase=0.0):
    w, h = 760, 520
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0)); g = ImageDraw.Draw(glow)
    cols = [PINK, (150, 80, 255), CYAN, PINK]
    k = (phase * 0.6) % 1.0
    c1 = cols[int(k * 3)]; c2 = cols[int(k * 3) + 1]; fr = (k * 3) % 1
    c = tuple(int(c1[i] * (1 - fr) + c2[i] * fr) for i in range(3))
    g.rounded_rectangle((60, 50, w - 60, h - 70), 40, fill=c + (255,))
    glow = glow.filter(ImageFilter.GaussianBlur(48))
    im.alpha_composite(glow); im.alpha_composite(glow)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((130, 100, w - 130, h - 130), 18, fill=(8, 8, 14), outline=(60, 60, 80), width=6)
    d.rounded_rectangle((150, 120, w - 150, h - 150), 10, fill=(20, 22, 40))
    d.rectangle((w / 2 - 40, h - 130, w / 2 + 40, h - 95), fill=(40, 40, 52))
    d.rounded_rectangle((w / 2 - 150, h - 98, w / 2 + 150, h - 82), 8, fill=(40, 40, 52))
    # LED strip along the back edge
    for i in range(16):
        x = 150 + i * (w - 300) / 15
        d.ellipse((x - 5, 96, x + 5, 106), fill=c + (255,))
    return im


def icon_headset(phase=0.0):
    w, h = 520, 480
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.arc((70, 20, w - 70, h - 40), 190, 350, fill=BLACK, width=58)
    d.arc((76, 26, w - 76, h - 46), 190, 350, fill=(235, 235, 240), width=40)
    for x0 in (40, w - 160):
        d.rounded_rectangle((x0, 210, x0 + 120, 400), 50, fill=BLACK)
        d.rounded_rectangle((x0 + 8, 218, x0 + 112, 392), 44, fill=(235, 235, 240))
        d.rounded_rectangle((x0 + 26, 240, x0 + 94, 370), 30, fill=(40, 40, 52))
    # mic boom flips up then back down
    a = math.radians(20 + 70 * max(0.0, math.sin(phase * 2.2)))
    bx, by = 100, 330
    ex, ey = bx + 190 * math.cos(a), by + 190 * math.sin(a) * -1 + 120 * (1 - math.sin(a))
    ex, ey = bx + 190 * math.cos(-a + math.radians(40)), by - 190 * math.sin(-a + math.radians(40))
    d.line((bx, by, ex, ey), fill=BLACK, width=26); d.line((bx, by, ex, ey), fill=(60, 60, 75), width=14)
    d.ellipse((ex - 22, ey - 22, ex + 22, ey + 22), fill=(60, 60, 75), outline=BLACK, width=5)
    return im


def icon_sdcard(label_top="microSD", label_bot="EXPRESS", col=YEL, cross=False):
    w, h = 300, 400
    im = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    poly = [(30, 0), (w, 0), (w, h), (0, h), (0, 150), (30, 120)]
    d.polygon([(x + 10, y + 14) for x, y in poly], fill=(0, 0, 0, 190))
    d.polygon(poly, fill=(28, 26, 40), outline=BLACK)
    d.line(poly + [poly[0]], fill=BLACK, width=8)
    d.rectangle((40, 30, w - 40, 210), fill=col)
    d.text((w / 2, 95), label_top, font=F(40), fill=BLACK, anchor="mm")
    d.text((w / 2, 160), label_bot, font=F(38), fill=BLACK, anchor="mm")
    for i in range(6):
        d.rounded_rectangle((44 + i * 38, h - 80, 64 + i * 38, h - 30), 4, fill=(210, 170, 60))
    if cross:
        d.line((10, 10, w - 10, h - 10), fill=RED, width=34); d.line((w - 10, 10, 10, h - 10), fill=RED, width=34)
    return im


def mascot(path, height):
    im = Image.open(path).convert("RGBA")
    if path.endswith("_cutout.png"):
        m = im
    else:  # white background: flood-fill from corners to transparent
        rgb = im.convert("RGB"); w, h = rgb.size
        mask = Image.new("L", (w + 2, h + 2), 0)
        a = np.array(rgb).astype(int)
        white = ((a[..., 0] > 238) & (a[..., 1] > 238) & (a[..., 2] > 238)).astype(np.uint8) * 255
        from scipy.ndimage import label
        lab, _ = label(white)
        border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
        bg = np.isin(lab, list(border))
        alpha = np.where(bg, 0, 255).astype(np.uint8)
        im.putalpha(Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(1)))
        m = trim(im)
    r = height / m.height
    return m.resize((int(m.width * r), height), Image.LANCZOS)


# ---------- backgrounds ----------

def glow_bg(seed=7):
    rng = np.random.default_rng(seed)
    big = Image.new("RGB", (int(W * 1.15), int(H * 1.15)), (14, 10, 28))
    lay = Image.new("RGB", big.size, (0, 0, 0)); d = ImageDraw.Draw(lay)
    for _ in range(16):
        c = [PINK, CYAN, (130, 70, 255), (255, 120, 60)][rng.integers(4)]
        x, y = rng.integers(0, big.width), rng.integers(0, big.height)
        r = rng.integers(120, 380)
        d.ellipse((x - r, y - r, x + r, y + r), fill=tuple(int(v * 0.42) for v in c))
    lay = lay.filter(ImageFilter.GaussianBlur(120))
    big = ImageChops.add(big, lay)
    # faint desk line and monitor silhouettes
    big = big.filter(ImageFilter.GaussianBlur(6))
    big = Image.blend(big, Image.new("RGB", big.size, (16, 11, 32)), 0.35)
    v = Image.new("L", big.size, 0); dv = ImageDraw.Draw(v)
    dv.ellipse((-big.width * 0.3, -big.height * 0.2, big.width * 1.3, big.height * 1.2), fill=255)
    v = v.filter(ImageFilter.GaussianBlur(200))
    dark = Image.new("RGB", big.size, (6, 4, 12))
    return Image.composite(big, dark, v)


def end_bg(color=(236, 72, 130)):
    im = Image.new("RGB", (W, H), color); d = ImageDraw.Draw(im)
    lc = tuple(min(255, int(v * 1.18)) for v in color)
    rng = np.random.default_rng(3)
    for _ in range(26):
        x, y = rng.integers(40, W - 40), rng.integers(40, H - 40); s = rng.integers(26, 46); k = rng.integers(4)
        if k == 0: d.ellipse((x - s, y - s, x + s, y + s), outline=lc, width=6)
        elif k == 1: d.polygon([(x, y - s), (x + s, y + s), (x - s, y + s)], outline=lc, width=6)
        elif k == 2: d.line((x - s, y - s, x + s, y + s), fill=lc, width=7); d.line((x + s, y - s, x - s, y + s), fill=lc, width=7)
        else: d.rounded_rectangle((x - s * 1.4, y - s * 0.7, x + s * 1.4, y + s * 0.7), 10, outline=lc, width=6)
    return im


def topbar(frame, tag):
    h = pill("@mygamerfeed", 34)
    frame.alpha_composite(h, (60, 272))
    if tag:
        t = pill(tag, 34, bg=YEL)
        frame.alpha_composite(t, (940 - t.width, 272))


def pop_scale(dt):
    if dt < 0: return 0.0
    if dt < 0.12: return 0.55 + 0.6 * (dt / 0.12)
    if dt < 0.22: return 1.15 - 0.15 * ((dt - 0.12) / 0.10)
    return 1.0


def ease_out(x):
    x = min(1.0, max(0.0, x)); return 1 - (1 - x) ** 3


def anim_state(kind, dt, seed):
    """Return (scale, dx, dy, angle, alpha) for an element dt seconds after it enters."""
    bob = 6 * math.sin(2 * math.pi * 0.7 * dt + seed)
    if kind == "slam":
        if dt < 0.14: sc = 1.9 - 0.95 * (dt / 0.14)
        elif dt < 0.26: sc = 0.95 + 0.05 * ((dt - 0.14) / 0.12)
        else: sc = 1.0
        ang = 2.2 * math.sin(2 * math.pi * 0.9 * dt + seed)
        return sc, 0, bob, ang, min(1, dt / 0.06)
    if kind in ("slide_l", "slide_r"):
        k = ease_out(dt / 0.22); sgn = -1 if kind == "slide_l" else 1
        return 1.0, sgn * 700 * (1 - k), bob, 0, 1
    if kind == "rise":
        k = ease_out(dt / 0.25)
        return 1.0, 0, 220 * (1 - k) + bob, 0, k
    if kind == "spin":
        k = ease_out(dt / 0.3)
        return pop_scale(dt), 0, bob, -180 * (1 - k), 1
    return pop_scale(dt), 0, bob, 1.2 * math.sin(2 * math.pi * 0.5 * dt + seed) if dt > 0.25 else 0, 1


def put(frame, sprite, cx, y, st):
    sc, dx, dy, ang, al = st
    if sc <= 0 or al <= 0: return
    sp = sprite
    if sc != 1.0: sp = sp.resize((max(1, int(sp.width * sc)), max(1, int(sp.height * sc))), Image.BILINEAR)
    if abs(ang) > 0.05: sp = sp.rotate(ang, resample=Image.BILINEAR, expand=True)
    if al < 1:
        a = sp.getchannel("A").point(lambda v: int(v * al)); sp = sp.copy(); sp.putalpha(a)
    ox = cx + dx - sp.width / 2
    oy = y + dy + (sprite.height - sp.height) / 2
    frame.alpha_composite(sp, (int(ox), int(oy)))


def particles(frame, t, rng_seed=5, n=16):
    rng = np.random.default_rng(rng_seed)
    layer = Image.new("RGBA", frame.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    for i in range(n):
        x0, sp, ph, sz, k = rng.uniform(0, W), rng.uniform(40, 90), rng.uniform(0, 1), rng.uniform(22, 40), rng.integers(4)
        y = (H + 100) - ((t * sp + ph * (H + 200)) % (H + 200))
        x = x0 + 30 * math.sin(t * 0.8 + i)
        c = (255, 255, 255, 60)
        if k == 0: d.ellipse((x - sz, y - sz, x + sz, y + sz), outline=c, width=5)
        elif k == 1: d.line((x - sz, y, x + sz, y), fill=c, width=6); d.line((x, y - sz, x, y + sz), fill=c, width=6)
        elif k == 2: d.polygon([(x, y - sz), (x + sz, y + sz), (x - sz, y + sz)], outline=c, width=5)
        else: d.rounded_rectangle((x - sz * 1.4, y - sz * 0.7, x + sz * 1.4, y + sz * 0.7), 10, outline=c, width=5)
    frame.alpha_composite(layer)


def place(frame, sprite, cx, y, s):
    put(frame, sprite, cx, y, (s, 0, 0, 0, 1))


def punch(frame, z):
    if z <= 1.001: return frame
    w2, h2 = int(W * z), int(H * z)
    big = frame.resize((w2, h2), Image.BILINEAR)
    return big.crop(((w2 - W) // 2, (h2 - H) // 2, (w2 - W) // 2 + W, (h2 - H) // 2 + H))


CX = 500  # content centre, left of the right-side action buttons


def build_sprite(it):
    ty = it["type"]; sz = it.get("size", 96)
    if ty == "white": return outlined_text(it["text"], sz, WHITE)
    if ty == "yellow": return outlined_text(it["text"], sz, YEL)
    if ty == "pill": return pill(it["text"], it.get("size", 46), bg=COLORS.get(it.get("color", "white"), WHITE))
    if ty == "sticker": return sticker(it["text"], it.get("size", 54), COLORS.get(it.get("color", "yellow"), YEL), it.get("angle", -4))
    if ty == "num": return num_badge(it["text"])
    if ty == "check": return check_row(it["text"], it.get("size", 54), it.get("ok", True))
    if ty == "img":
        im = Image.open(os.path.join(ASSETS, it["path"])).convert("RGBA"); r = it["h"] / im.height
        return im.resize((int(im.width * r), it["h"]), Image.LANCZOS)
    if ty == "sd": return icon_sdcard(cross=it.get("cross", False), col=COLORS.get(it.get("color", "yellow"), YEL),
                                      label_top=it.get("top", "microSD"), label_bot=it.get("bot", "EXPRESS"))
    return None


def render(spec, out):
    vo_path = spec["vo"]
    vo = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", vo_path, "-af", "pan=mono|c0=c0", "-ar", str(SR), "-f", "f32le", "-"],
                                      capture_output=True).stdout, np.float32).copy()
    vo_len = len(vo) / SR
    total = vo_len + spec.get("tail", 1.2)
    nfr = int(math.ceil(total * FPS))
    bg = glow_bg(spec.get("seed", 7)); ebg = end_bg()
    merch = Image.open(os.path.join(ASSETS, spec.get("merch_card", "endcards/mgf-merch-endcard-blackfriday.png"))).convert("RGBA")
    # pre-build sprites
    for sc in spec["scenes"]:
        for it in sc.get("items", []):
            if it["type"] not in ("tv", "headset"):
                it["_s"] = build_sprite(it)
    thumbs = mascot(os.path.join(ASSETS, "mascot_ref_thumbs.png"), 420)
    # cover
    cv = spec["cover"]
    cover = bg.crop((0, 0, W, H)).convert("RGBA").filter(ImageFilter.GaussianBlur(2))
    topbar(cover, spec.get("tag"))
    l1 = outlined_text(cv["l1"], 120, WHITE); l2 = outlined_text(cv["l2"], 120, YEL)
    place(cover, l1, CX, 380, 1); place(cover, l2, CX, 380 + l1.height + 4, 1)
    st = sticker(cv["stamp"], 66, COLORS[cv.get("stamp_color", "yellow")], -5)
    place(cover, st, CX, 380 + l1.height + l2.height + 40, 1)
    pose = mascot(os.path.join(ASSETS, "poses", "mgf_pose_%s_cutout.png" % cv.get("pose", "laughing_a")), 620)
    cover.alpha_composite(pose, (int(CX - pose.width / 2), 1480 - pose.height))
    os.makedirs("frames_tmp", exist_ok=True)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "video_tmp.mp4"], stdin=subprocess.PIPE)
    events = sorted({it["t"] for sc in spec["scenes"] for it in sc.get("items", [])} | {sc["t0"] for sc in spec["scenes"]})
    starts = [sc["t0"] for sc in spec["scenes"]]
    for fi in range(nfr):
        t = fi / FPS
        if t < 0.2:
            enc.stdin.write(cover.convert("RGB").tobytes()); continue
        sc = next((s for s in spec["scenes"] if s["t0"] <= t < s["t1"]), spec["scenes"][-1])
        st0 = sc["t0"]
        if sc["kind"] == "merch":
            fr = Image.new("RGBA", (W, H), NAVY + (255,))
            z = 1.0 + 0.05 * ((t - st0) / max(0.1, sc["t1"] - st0))
            m = merch.resize((int(W * z), int(H * z)), Image.BILINEAR)
            fr.alpha_composite(m, ((W - m.width) // 2, (H - m.height) // 2))
            for it in sc.get("items", []):
                if t < it["t"] or t >= it.get("until", 1e9) or it["type"] == "beat": continue
                dt = t - it["t"]
                if it["type"] == "box":
                    x, y, s_ = it["box"]; cxm, cym = W / 2, H / 2
                    X0 = cxm + (x - cxm) * z; Y0 = cym + (y - cym) * z; S = s_ * z
                    pulse = 1 + 0.04 * math.sin(dt * 10) * math.exp(-dt * 2)
                    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dg = ImageDraw.Draw(g)
                    pad = 10 + 6 * pulse
                    dg.rounded_rectangle((X0 - pad, Y0 - pad, X0 + S + pad, Y0 + S + pad), 34, outline=YEL + (255,), width=12)
                    fr.alpha_composite(g.filter(ImageFilter.GaussianBlur(6))); fr.alpha_composite(g)
                else:
                    put(fr, it["_s"], it.get("x", CX), it["y"], anim_state(it.get("anim", "slam"), dt, it["t"]))
        elif sc["kind"] == "end":
            fr = ebg.convert("RGBA").copy(); particles(fr, t, 9, 12)
            y = 360; dt = t - st0
            for i, ln in enumerate(sc["question"]):
                sp = outlined_text(ln, 88, WHITE if i == 0 else YEL); put(fr, sp, CX, y, anim_state("slam" if i else "pop", dt - 0.1 * i, i)); y += sp.height + 2
            y += 30
            put(fr, thumbs, CX, y, anim_state("rise", dt - 0.1, 2)); y += thumbs.height + 20
            for i, ln in enumerate(sc["follow"]):
                sp = outlined_text(ln, 58, WHITE if i == 0 else YEL, stroke=7); put(fr, sp, CX, y, anim_state("pop", dt - 0.2 - 0.08 * i, 3 + i)); y += sp.height
            ex = sc.get("extra")
            if ex and t >= ex["t"]:
                sp = pill(ex["text"], 46, bg=YEL); put(fr, sp, CX, y + 24, anim_state("slam", t - ex["t"], 5))
            if sc.get("next"):
                sp = pill(sc["next"], 40, bg=WHITE); put(fr, sp, CX, 1400, anim_state("slide_r", dt - 0.3, 6))
        else:
            ox = int((bg.width - W) / 2 + 60 * math.sin(t * 0.35)); oy = int((bg.height - H) / 2 + 45 * math.cos(t * 0.27))
            fr = bg.crop((ox, oy, ox + W, oy + H)).convert("RGBA")
            particles(fr, t)
            for it in sc["items"]:
                if t < it["t"] or t >= it.get("until", 1e9) or it["type"] == "beat": continue
                dt = t - it["t"]; kind = it.get("anim", {"num": "spin", "sticker": "slam", "pill": "slide_l", "check": "slide_l", "sd": "rise", "img": "rise", "tv": "rise", "headset": "rise"}.get(it["type"], "pop"))
                st = anim_state(kind, dt, it["t"])
                if it["type"] == "tv": put(fr, icon_tv(t), CX, it["y"], st); continue
                if it["type"] == "headset":
                    hi = icon_headset(dt); k = it.get("scale", 1.0)
                    if k != 1.0: hi = hi.resize((int(hi.width * k), int(hi.height * k)), Image.BICUBIC)
                    put(fr, hi, CX, it["y"], st); continue
                if it.get("shake_at") and t >= it["shake_at"]:
                    sd = t - it["shake_at"]
                    if sd < 0.35: st = (st[0], st[1] + 14 * math.sin(sd * 60) * (1 - sd / 0.35), st[2], st[3], st[4])
                if it.get("align") == "left":
                    put(fr, it["_s"], it.get("x", 110) + it["_s"].width / 2, it["y"], st)
                else:
                    put(fr, it["_s"], it.get("x", CX), it["y"], st)
        # camera punch on every new element, bigger zoom-flash on scene changes
        z = 1.0
        for te in events:
            if 0 <= t - te < 0.3: z = max(z, 1 + 0.03 * math.exp(-(t - te) / 0.09))
        for ts_ in starts:
            if 0 <= t - ts_ < 0.25: z = max(z, 1 + 0.09 * (1 - ease_out((t - ts_) / 0.25)))
        fr = punch(fr, z)
        for ts_ in starts:
            if 0 <= t - ts_ < 0.07:
                fr = Image.blend(fr, Image.new("RGBA", (W, H), (255, 255, 255, 255)), 0.22)
        if sc["kind"] != "merch": topbar(fr, spec.get("tag") if sc["kind"] != "end" else None)
        enc.stdin.write(fr.convert("RGB").tobytes())
    enc.stdin.close(); enc.wait()
    # audio: voice untouched, music bed 0.055 under voice, rises to 0.15 after the voice, short fade
    n = int(total * SR)
    mus = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-ss", str(spec.get("music_offset", 0)), "-i", spec["music"], "-ac", "1", "-ar", str(SR),
                                        "-t", str(total + 0.5), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)[:n]
    tt = np.arange(n) / SR
    env = np.interp(tt, [0, 0.2, 0.5, vo_len, vo_len + 0.35, total - 0.6, total], [0, 0, 0.055, 0.055, 0.15, 0.15, 0])
    voice = np.zeros(n, np.float32); voice[:len(vo)] = vo[:n]
    mix = voice + mus * env
    def lufs(x):
        p = subprocess.run(["ffmpeg", "-v", "info", "-nostats", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-af", "ebur128", "-f", "null", "-"],
                           input=np.stack([x, x], 1).astype(np.float32).tobytes(), capture_output=True).stderr.decode()
        return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", p)[-1])
    g = 10 ** ((spec.get("target_lufs", -21.0) - lufs(mix)) / 20)
    pk = np.abs(mix).max() * g
    if pk > 10 ** (-4 / 20): g *= 10 ** (-4 / 20) / pk
    mix = mix * g
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_s24le", "audio_tmp.wav"],
                   input=np.stack([mix, mix], 1).astype(np.float32).tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "video_tmp.mp4", "-i", "audio_tmp.wav", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
                    "-shortest", "-movflags", "+faststart", out])
    print(json.dumps({"out": out, "dur": round(total, 2), "gain": round(float(g), 3), "lufs_target": spec.get("target_lufs", -21.0)}))


if __name__ == "__main__":
    render(json.load(open(sys.argv[1])), sys.argv[2])
