"""Cut-only voiceover edit. Usage: python3 vo_cut.py SOURCE.wav plan.json OUT.wav OUT_pieces.json
plan.json: list of [start,end] rough seconds (from transcript) in SOURCE, kept in order.
Each edge is snapped into a real silence (below THR dB). Pauses inside a piece longer than MAXP are
shortened to KEEP by cutting out their middle. Joins get 15 ms fades. Voice is never processed.
Uses the LEFT channel only."""
import sys, json, subprocess, numpy as np
src, planf, out, piecesf = sys.argv[1:5]
THR = -45.0; PTH = -38.0; MAXP = 0.34
sr = 48000
x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-af', 'pan=mono|c0=c0', '-ar', str(sr), '-f', 'f32le', '-'],
                                 capture_output=True).stdout, np.float32).copy()
h = 480; n = len(x) // h
e = 20 * np.log10(np.sqrt((x[:n * h].reshape(n, h) ** 2).mean(1)) + 1e-9)
q = e < PTH
R = []; i = 0
while i < n:
    if q[i]:
        j = i
        while j < n and q[j]: j += 1
        if j - i >= 8: R.append((i, j))
        i = j
    else: i += 1
def quiet(a, b):
    a, b = max(0, int(a)), min(n, int(b))
    k = a + int(np.argmin(e[a:b])); return k
warn = []
def chk(k, what):
    if e[k] > THR: warn.append(f'{what} at {k/100:.2f}s is {e[k]:.0f} dB')
def snap_start(t):
    f = t * 100
    c = [(a, b) for a, b in R if f - 80 <= b <= f + 80]
    if not c: raise SystemExit(f'no pause before start {t:.2f}')
    a, b = min(c, key=lambda r: abs(r[1] - f))
    k = quiet(max(a, b - 20), b - 5); chk(k, 'start'); return k / 100
def snap_end(t):
    f = t * 100
    c = [(a, b) for a, b in R if f - 80 <= a <= f + 80]
    if not c: raise SystemExit(f'no pause after end {t:.2f}')
    a, b = min(c, key=lambda r: abs(r[0] - f))
    k = quiet(a + 5, min(b, a + 20)) + 1; chk(k - 1, 'end'); return k / 100
plan = json.load(open(planf)); pieces = []
for s, t in plan:
    a, b = snap_start(s), snap_end(t)
    cur = a
    for ra, rb in R:
        if ra / 100 > a + 0.05 and rb / 100 < b - 0.05 and (rb - ra) / 100 > MAXP:
            k1 = quiet(ra + 5, ra + 20) + 1; k2 = quiet(rb - 20, rb - 5)
            chk(k1 - 1, 'pause cut'); chk(k2, 'pause cut')
            pieces.append([cur, k1 / 100]); cur = k2 / 100
    pieces.append([cur, b])
for w in warn: print('WARN', w)
fade = int(0.015 * sr); outa = []
for a, b in pieces:
    seg = x[int(a * sr):int(b * sr)].copy()
    seg[:fade] *= np.linspace(0, 1, fade); seg[-fade:] *= np.linspace(1, 0, fade)
    outa.append(seg)
y = np.concatenate(outa)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(sr), '-ac', '1', '-i', '-', '-c:a', 'pcm_s24le', out],
               input=y.astype(np.float32).tobytes(), check=True)
json.dump([[round(a, 3), round(b, 3)] for a, b in pieces], open(piecesf, 'w'))
print(f'{len(pieces)} pieces, {len(y) / sr:.2f}s')
