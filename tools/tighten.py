"""Remove breaths and tighten pauses in an approved voiceover edit, without touching the voice itself.
Usage: python3 tighten.py IN.wav OUT.wav [GAP=0.16] [LONGGAP=0.24]
Speech islands = voiced or loud frames; everything between islands (breaths, room tone) is dropped and
replaced by digital silence of GAP seconds (LONGGAP where the original pause was over 0.6 s).
Prints a report of every edge so clipped sounds can be checked: an edge flagged LOUD-EDGE means the
audio just outside the kept region was above -42 dB (possible clipped word), re-check it by ear/transcript."""
import sys, subprocess, numpy as np
src, out = sys.argv[1], sys.argv[2]
GAP = float(sys.argv[3]) if len(sys.argv) > 3 else 0.16
LONG = float(sys.argv[4]) if len(sys.argv) > 4 else 0.24
sr = 48000
x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-f', 'f32le', '-ac', '1', '-ar', str(sr), '-'], capture_output=True).stdout, np.float32).copy()
h = 480; n = len(x) // h
fr = x[:n * h].reshape(n, h)
e = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9)
win = np.hanning(h)
F = np.abs(np.fft.rfft(fr * win, axis=1)); f = np.fft.rfftfreq(h, 1 / sr)
cent = (F * f).sum(1) / (F.sum(1) + 1e-9)
low = (F[:, f < 1000] ** 2).sum(1) / ((F ** 2).sum(1) + 1e-12)   # share of energy under 1 kHz
voiced = (e > -42) & (low > 0.5)
loud = e > -40                     # loud enough to be speech even if unvoiced (s, sh, t)
sp = voiced | loud
# merge islands across short dips (inside words / between words)
isl = []; i = 0
while i < n:
    if sp[i]:
        j = i
        while j < n:
            if sp[j]: j += 1; continue
            k = j
            while k < n and not sp[k]: k += 1
            if k - j <= 14 and k < n: j = k; continue   # gap <= 0.14 s stays inside the island
            break
        isl.append([i, j]); i = j
    else: i += 1
# drop tiny islands with no voicing (clicks, short breath bursts)
isl = [[a, b] for a, b in isl if voiced[a:b].sum() >= 3 or (b - a) >= 12 or e[a:b].max() > -38]
# extend edges: onsets back up to 60 ms, tails forward up to 150 ms while above -50 dB
for s in isl:
    a, b = s
    k = a
    while k > 0 and (e[k - 1] > -42 or (a - k < 6 and e[k - 1] > -50)): k -= 1
    s[0] = k
    k = b
    while k < n and (e[k] > -42 or (k - b < 15 and e[k] > -50)): k += 1
    s[1] = k
# trim breaths stuck to island edges: unvoiced stretches below -36 dB (fricatives are louder and short)
strong = voiced | (e > -34)
for s in isl:
    a, b = s
    k = b
    while k > a and not strong[k - 1]: k -= 1       # last strong frame
    if b - k > 18: s[1] = k + 15                      # >0.18 s weak tail: keep 150 ms (t/k release after closure)
    k = a
    while k < s[1] and not strong[k]: k += 1          # first strong frame
    if k - a > 18: s[0] = k - 15                      # >0.18 s weak lead-in: keep 150 ms (h, f, th onsets)
# make sure extended islands don't overlap
m = []
for a, b in isl:
    if m and a <= m[-1][1] + 2: m[-1][1] = max(m[-1][1], b)
    else: m.append([a, b])
isl = m
F10 = int(0.010 * sr)
o = []; rep = []
for idx, (a, b) in enumerate(isl):
    seg = x[a * h:b * h].copy(); r = np.linspace(0, 1, F10); seg[:F10] *= r; seg[-F10:] *= r[::-1]
    if idx:
        g0 = (a - isl[idx - 1][1]) / 100
        g = min(g0, LONG if g0 > 0.6 else GAP)
        pa, pb = isl[idx - 1][1], a
        rep.append(f'        drop {pa/100:7.2f}-{pb/100:7.2f} ({g0:.2f}s, max {e[pa:pb].max() if pb>pa else -99:5.0f} dB) -> {g:.2f}s')
        o.append(np.zeros(int(g * sr), np.float32))
    o.append(seg)
    pre = e[max(0, a - 3):a].max() if a > 0 else -99
    post = e[b:b + 3].max() if b < n else -99
    flag = ' LOUD-EDGE' if max(pre, post) > -42 else ''
    rep.append(f'{a/100:7.2f}-{b/100:7.2f} keep  outside pre {pre:5.0f} dB post {post:5.0f} dB{flag}')
y = np.concatenate(o)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(sr), '-ac', '1', '-i', '-', '-c:a', 'pcm_s24le', out], input=y.astype(np.float32).tobytes())
print('\n'.join(rep))
print(f'in {len(x)/sr:.2f}s -> out {len(y)/sr:.2f}s, {len(isl)} islands, {sum("LOUD-EDGE" in r for r in rep)} loud edges')
