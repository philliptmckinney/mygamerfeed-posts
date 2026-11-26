# reelkit (Nov 26)

Saved here so any chat can rebuild a reel. Nothing in a chat's workspace survives the chat.

- build_reel.py: spec JSON -> finished reel (cover frame, house-style scenes, merch card, end card, music mix at -21 LUFS).
  `MGF_ASSETS=assets python3 tools/reelkit/build_reel.py specs/<name>.json out.mp4` (vo and music paths in the spec).
- vo_cut_pieces.py: cut a bounce into pieces at silent points, tighten pauses, 15 ms fades. Check with tools/qa_vo.py.
- music_match.py: find which library track and offset a finished reel uses.
- music_stem.py + insert_cta.py: split voice from music in a finished reel and insert a line with the music continuous.
Rule: no reel ships until its spec is in specs/.
