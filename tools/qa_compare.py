"""Check a tightened voiceover against the version it came from: same words, nothing clipped, no breaths left.
Usage: python3 qa_compare.py BEFORE.wav AFTER.wav WHISPER_MODEL_DIR
1. Transcribes both and diffs the word lists (any dropped or changed word is printed).
2. Lists leftover breath-like stretches in AFTER: >=0.12 s, -58..-36 dB, mostly above 1 kHz, not next to speech."""
import sys, subprocess, difflib, re, numpy as np
from faster_whisper import WhisperModel
a, b, md = sys.argv[1:4]
m = WhisperModel(md, device='cpu', compute_type='int8')
def load(p, sr):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)
def words(p):
    segs, _ = m.transcribe(load(p, 16000), language='en', beam_size=5, condition_on_previous_text=False)
    t = ' '.join(s.text for s in segs).lower()
    return re.findall(r"[a-z0-9']+", t)
wa, wb = words(a), words(b)
bad = []
for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, wa, wb).get_opcodes():
    if op != 'equal': bad.append(f'{op}: before "{" ".join(wa[max(0,i1-3):i2+3])}"  after "{" ".join(wb[max(0,j1-3):j2+3])}"')
print(f'words before {len(wa)}, after {len(wb)}')
print('WORDS MATCH' if not bad else 'WORD DIFFS (check by ear):'); [print(' -', x) for x in bad]
sr = 48000; x = load(b, sr); h = 480; n = len(x) // h
fr = x[:n * h].reshape(n, h); e = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9)
F = np.abs(np.fft.rfft(fr * np.hanning(h), axis=1)); f = np.fft.rfftfreq(h, 1 / sr)
low = (F[:, f < 1000] ** 2).sum(1) / ((F ** 2).sum(1) + 1e-12)
br = (e > -58) & (e < -36) & (low < 0.5)
spch = (e > -36) | ((e > -45) & (low > 0.5))
out = []; i = 0
while i < n:
    if br[i]:
        j = i
        while j < n and br[j]: j += 1
        near = spch[max(0, i - 3):i].any() or spch[j:j + 3].any()
        if j - i >= 12 and not near: out.append(f'{i/100:.2f}-{j/100:.2f} ({(j-i)/100:.2f}s, max {e[i:j].max():.0f} dB)')
        i = j
    else: i += 1
print('NO BREATHS LEFT' if not out else 'POSSIBLE BREATHS:'); [print(' -', s) for s in out]
