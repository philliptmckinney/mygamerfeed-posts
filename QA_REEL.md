# Reel QA: independent reviewer pass

Every reel gets this check from a fresh reviewer agent before it is scheduled in Buffer.
The reviewer gets only the finished MP4, the script, the caption, the titles and the source links.
It does not see how the reel was built, so it is not grading its own work.

## Voiceover edit QA (before any edit goes to Tyler)

Run `python3 tools/qa_vo.py <bounce.wav> pieces.json <bounce words.json>` on every edit, then transcribe the edited file and read it against the script.
- Every cut edge is quiet (below -45 dB) or is a deliberate mid-phrase join that has been checked by transcript.
- No cut lands inside a word. No word or partial word repeats across a join (the "and f, and for once" error).
- Every scripted line and every ad-lib Tyler added is present, unless he approved cutting it. Never drop his ad-libs to save time without asking.
- The transcript of the edit reads as the script, in order, with nothing clipped at either end.
Only send the edit once this passes. If it flags something, fix it and run it again first.

## Recording rhythm (agreed Nov 5)

- One weekly batch session covers 7 to 10 days of evergreen scripts: countdown episodes, stories, explainers, long-form. Tyler says the script number before each one.
- Daily carousels carry the day's news with no voiceover.
- Breaking news gets a short script (about 30 seconds) sent to Tyler the same day, recorded in about 5 minutes on the Wireless GO 2. Only for news worth it, about 2 or 3 a week.
- Freshness check: before any batched script posts, re-verify its facts against current news. If something changed, adjust the caption and on-screen text, flag it to Tyler, or swap in another script. Never post a stale "today" or "just announced" line.

## What the reviewer checks

1. Length: under 58 seconds (YouTube blocks claimed Shorts over 60 seconds worldwide).
2. Audio:
   - Voice is Tyler's bounce, untouched, with no clipped starts or ends.
   - Music bed has no gaps, drops or loops (RMS check every 0.5 seconds across the whole bed).
   - Music sits under the voice and rises on the end card only.
   - Track has not been claimed before on our channel (see the claimed-track list below).
3. Picture: frames at every scene change plus 1 second in.
   - No cut-off, overlapping or misspelled text.
   - Cover frame is the first frame; the end card reads "Subscribe so you don't miss Day N" where it applies.
   - Footage labeled 1998 or N64 is Tyler's real capture; everything else is official press material.
4. Facts: every number, name, date and quote on screen, in the voice, caption and title matches an opened source.
   Labels are honest (CONFIRMED, REPORTED, UNCONFIRMED). "Rockstar says" only for official Rockstar statements;
   preview-visit claims are "Rockstar told preview visitors."
5. Text rules: no em dashes anywhere, proper capitalization, at most 5 hashtags, YouTube title under 60 characters,
   TikTok caption opens with the search phrase.
6. Countdown episodes: day number is correct for the posting date, and the tease line matches the next episode.
7. Retention (from the Nov 3 Instagram insights on the Zelda lengths reel: half of viewers gone by 6 seconds, flat middle, drop at the end card):
   - The payoff number or headline is on screen in the first second, not after an intro.
   - Data reels reach the chart within 3 seconds.
   - The closing question and the follow card are one combined card of about 2 seconds.
   - The script has one natural share line ("Send this to...") before the closing question.
8. Safe zones: no text or pills in the top 260 px (Instagram back arrow and + button, TikTok top bar) or the bottom 420 px and right 140 px (captions and action buttons).
   One source credit only.

## Output

PASS, or a numbered list of fixes with timestamps. Fix, re-render, and re-run the check before scheduling.

## Claimed-track list (do not use on YouTube)

- Ghost Beatz, "Daybreak" (claimed Nov 2 on the Hum Short)
