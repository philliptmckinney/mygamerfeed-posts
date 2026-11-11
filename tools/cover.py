"""Grid-friendly cover frame with the mascot, built over a blurred, darkened copy of the reel's first frame.
Usage: python3 cover.py SPEC_NAME   (specs below). Writes cover/<name>.png and a TikTok-grid preview."""
import sys, os
S = '/tmp/claude-0/-home-claude/84d9a987-6211-59bf-b239-4931e378b385/scratchpad'
sys.path.insert(0, S)
from kit import *
from PIL import Image, ImageFilter, ImageDraw, ImageEnhance
POSE = '/home/claude/mygamerfeed-posts/assets/poses/mgf_pose_%s_cutout.png'
F0 = S + '/cover/f0/%s.png'

def stamp(txt, size, col):
    f = font(size); tw = int(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(txt, font=f))
    im = Image.new("RGBA", (tw + 80, size + 70), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 6, tw + 74, size + 64), 18, fill=(255, 255, 255, 235), outline=col, width=10)
    d.text(((tw + 80) / 2, (size + 70) / 2), txt, font=f, fill=col, anchor="mm"); return im

SPECS = {
 '2026-11-11-mw4-camos':       dict(l1="YOUR CAMOS", l2="DIDN'T COME", stamp="BO7 GUNS: IN", scol=GREEN, pose='shocked_b', side='left', corner=None, cred="IMAGES: ACTIVISION"),
 '2026-11-12-ocarina-missing': dict(l1="96 ON METACRITIC", l2="BUT IT'S MISSING", stamp="MISSING: 3", scol=RED, pose='shocked_a', side='left', corner="2026 REMAKE", cred="FOOTAGE: NINTENDO"),
 '2026-11-13-gta6-day6-spoiler-shield': dict(l1="THE ENDING", l2="WILL LEAK", stamp="SPOILER ALERT", scol=RED, pose='shocked_b', side='left', corner="GTA 6 IN 6 DAYS", cred="FOOTAGE: ROCKSTAR GAMES"),
 '2026-11-13-warzone-switch2': dict(l1="WARZONE", l2="ON SWITCH 2", stamp="FREE", scol=RED, pose='shocked_a', side='right', corner=None, cred="IMAGES: ACTIVISION"),
 '2026-11-14-mw4-battle-pass': dict(l1="IT CATCHES YOU UP", l2="MW4 BATTLE PASS", stamp="FINALLY", scol=GREEN, pose='laughing_a', side='left', corner=None, cred="IMAGES: ACTIVISION"),
 '2026-11-15-ocarina-nine-ways': dict(l1="9 VERSIONS", l2="ONLY 2 REMAKES", stamp="SINCE 1998", scol=GREEN, pose='thinking_a', side='right', corner="2026 REMAKE", cred="FOOTAGE: NINTENDO"),
}

BG = {'2026-11-11-mw4-camos': 'press/mw4/img/mobile-wallpapers__COD_MW4_GHOST.jpg', '2026-11-12-ocarina-missing': 'r_missing/navi/f0001.jpg', '2026-11-13-gta6-day6-spoiler-shield': 'r_spoil/pair/f0001.jpg', '2026-11-13-warzone-switch2': 'r_warzone/img/ghost.jpg', '2026-11-14-mw4-battle-pass': 'press/mw4/img/mobile-wallpapers__COD_MW4_GHOST_HA.jpg', '2026-11-15-ocarina-nine-ways': 'r_nine/hook/f0001.jpg'}

def fit(path):
    im = Image.open(S + '/' + path).convert('RGB'); w, h = im.size
    if w / h > 9 / 16:
        tw = int(h * 9 / 16); im = im.crop(((w - tw) // 2, 0, (w - tw) // 2 + tw, h))
    else:
        th = int(w * 16 / 9); im = im.crop((0, (h - th) // 2, w, (h - th) // 2 + th))
    return im.resize((W, H), Image.LANCZOS)

def build(name):
    sp = SPECS[name]
    bg = fit(BG[name]); bg.paste(Image.new('RGB', (W, H), INK), (0, 0), E.shade())
    bg = ImageEnhance.Brightness(bg).enhance(0.8)
    c = bg.convert('RGBA')
    m = Image.open(POSE % sp['pose']).convert('RGBA')
    h = 800; m = m.resize((int(m.width * h / m.height), h), Image.LANCZOS)
    if m.width > 620: m = m.resize((620, int(m.height * 620 / m.width)), Image.LANCZOS)
    y = 1470 - m.height
    x = -40 if sp['side'] == 'left' else W - m.width + 40
    sh = Image.new('RGBA', m.size, (0, 0, 0, 0)); sh.putalpha(m.split()[-1].point(lambda a: int(a * 0.6)))
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    c.alpha_composite(sh, (x + 14, y + 20)); c.alpha_composite(m, (x, y))
    place(c, text_sprite(sp['l1'], 128, WHITE, 12, maxw=900), CX, 470, 1.0, 1.0, rot=-2)
    place(c, text_sprite(sp['l2'], 112, YELLOW, 12, maxw=900), CX, 610, 1.0, 1.0, rot=-2)
    st = stamp(sp['stamp'], 78, sp['scol']); hw = st.width / 2 + 20
    sx = 940 - hw if sp['side'] == 'left' else max(hw + 20, 300)
    place(c, st, sx, 900, 1.0, 1.0, rot=-6 if sp['side'] == 'left' else 6)
    handle(c)
    if sp['corner']: corner(c, sp['corner'])
    credit(c, sp['cred'])
    c = c.convert('RGB'); c.save(S + '/cover/%s.png' % name)
    return c

if __name__ == '__main__':
    names = sys.argv[1:] or list(SPECS)
    ims = [build(n) for n in names]
    sheet = Image.new('RGB', (len(ims) * 400 + 20, 560), (30, 30, 30))
    for i, im in enumerate(ims):
        sheet.paste(im.crop((0, 240, 1080, 1680)).resize((390, 520)), (i * 400 + 10, 20))
    sheet.save(S + '/cover/grid_preview.jpg', quality=85)
    print('ok', names)
