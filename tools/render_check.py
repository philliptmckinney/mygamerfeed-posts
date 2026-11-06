"""@mygamerfeed checklist carousel: cover, one checklist step per slide, follow.
Usage: python3 render_check.py check.json outdir
check.json: {"title":[l1,l2],"sub":...,"hook":...,"color":[r,g,b],"source":...,
             "steps":[{"head":...,"body":...}], "avatar_point":..., "avatar_thumbs":...}
"""
import json, os, sys
from PIL import Image, ImageDraw
from render_bright import rubik, wrap, confetti, card, pill, topbar, swipe, follow, INK, WHITE, YELLOW, TEXT2
from render_rank import cover, TIER_COLORS, W, H


def step(s, n, i, total, source):
    c = TIER_COLORS[(i - 2) % len(TIER_COLORS)]
    img = Image.new("RGB", (W, H), c)
    confetti(img, c, i * 17)
    d = ImageDraw.Draw(img)
    topbar(d, W, i, total)
    M, P = 60, 56
    hf, bf = rubik(72), rubik(42, "Medium")
    hl = wrap(d, s["head"], hf, W - 2 * M - 2 * P)
    bl = wrap(d, s["body"], bf, W - 2 * M - 2 * P)
    ch = P + 110 + 36 + len(hl) * 82 + 26 + len(bl) * 56 + P
    y0 = max(190, (H - ch) // 2 - 20)
    card(d, [M, y0, W - M, y0 + ch])
    x, y = M + P, y0 + P
    d.rounded_rectangle([x + 6, y + 6, x + 116, y + 116], 24, fill=INK)
    d.rounded_rectangle([x, y, x + 110, y + 110], 24, fill=(32, 190, 90), outline=INK, width=5)
    d.line([(x + 26, y + 58), (x + 48, y + 82), (x + 88, y + 30)], fill=WHITE, width=14, joint="curve")
    pill(d, x + 140, y + 26, f"STEP {n}", YELLOW, rubik(34), h=60, pad=24)
    y += 110 + 36
    for line in hl:
        d.text((x, y), line, font=hf, fill=INK); y += 82
    y += 26
    for line in bl:
        d.text((x, y), line, font=bf, fill=TEXT2); y += 56
    d.text((64, H - 112), source, font=rubik(30, "Bold"), fill=WHITE, stroke_width=3, stroke_fill=INK)
    if i < total:
        swipe(d, W, H)
    return img


def main():
    data = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    total = len(data["steps"]) + 2
    slides = [cover(data, total)] + [step(s, k + 1, k + 2, total, data["source"]) for k, s in enumerate(data["steps"])]
    slides.append(follow(W, H, total, data.get("avatar_thumbs")))
    for n, s in enumerate(slides, 1):
        s.save(os.path.join(out, f"{n:02d}.jpg"), quality=92)
    print(total, "slides")


if __name__ == "__main__":
    main()
