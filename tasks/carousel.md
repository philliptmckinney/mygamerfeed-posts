You are producing and PUBLISHING a gaming news carousel for Tyler's page @mygamerfeed through Buffer. This task runs once a day at 11:38 AM Central and posts to TikTok ONLY. Do not post anything to Instagram: Instagram carousels got 0 to 1 views each, so Tyler stopped them on Nov 4 (voiced reels go to Instagram from a separate session). Tyler wants this fully automatic: do the whole job, verify it, and publish without asking him or waiting for approval. Because nobody reviews it first, the VERIFY step is mandatory: if anything fails verification and you cannot fix it with certainty, publish nothing and tell him why. Never generate AI voice, image or video.

1. TIME WINDOW. Get the current date and time with current_time. Your window is the last 24 hours. Only use stories first reported, or meaningfully updated, inside it. Call Buffer list_posts (organization 6adfbc17399e3947f020b7bc, newest first, about 10 posts) and skip any story already covered in a recent post unless there is a major new development.

2. RESEARCH. Run many WebSearch queries together across gaming outlets (IGN, VGC, Game Informer, PC Gamer, GamesRadar, Eurogamer, Kotaku, Polygon, Push Square, Pure Xbox, Nintendo Life, GamesIndustry.biz, Insider Gaming), tech outlets and official newsrooms (The Verge, Digital Foundry, Engadget, NVIDIA, AMD, Sony, Microsoft, Nintendo, Valve, Rockstar Newswire), mobile (Pocket Gamer, TouchArcade), and outlet coverage of leaks and insider chatter ("leak", "rumor", "insider" plus the platform or game). Include lawsuits, closures and layoffs, AI in games, big releases. Skip deals, guides and filler. Lead with huge franchises (GTA, Nintendo, PlayStation, Xbox, Call of Duty, Pokémon, Fortnite, Minecraft).

3. DECIDE. If fewer than 3 solid stories fall inside the window, render and post nothing; write one `info` document to Gamer Feed HQ (source "Carousel", title "No carousel today", body "Not enough new gaming news in the last 24 hours.") and stop. Otherwise pick the best 3 to 5, newest and biggest first.

4. LABEL HONESTLY: CONFIRMED (official, or reported as fact by multiple reputable outlets), REPORTED (one credible outlet citing sources), UNCONFIRMED (leaks, insiders, forums, speculation). Never present an unconfirmed story as fact. Preview-visit claims are "Rockstar told preview visitors", not "Rockstar says".

5. WRITE per story: tag (PC, CONSOLE, HANDHELD, MOBILE, INDUSTRY, HARDWARE, AI, LEGAL or RELEASE), status, short (cover teaser under 36 characters), head (under about 60 characters), body (one or two plain sentences under about 140 characters), source (outlet names). Proper capitalization, full sentences, never em dashes, your own words only, never promise a posting frequency, no slogans or rule-of-three taglines. TikTok caption: a one-sentence hook naming the 2 or 3 biggest stories plus "Swipe for today's gaming news. Follow @mygamerfeed to stay in the loop.", a blank line, no more than 5 hashtags. Also a short TikTok title like "Today in Gaming: Nov 4" (vary the hook wording day to day).

6. RENDER.
a) Fonts: mkdir -p /home/claude/fonts && cd /home/claude/fonts && curl -sSfL -o Rubik.ttf "https://raw.githubusercontent.com/google/fonts/main/ofl/rubik/Rubik%5Bwght%5D.ttf"
b) Mascot: pick two random numbers 1 to 4 with python (pointing pose N, thumbs-up pose M). Use the Artifact tool, action "read", url "https://claude.ai/artifact/MDXhqqRYHipmWJKo2QdUyu", paths ["point_N.png", "thumbs_M.png"]. Note where it saved them. Pointing pose on the cover, thumbs-up on the follow slide. Never change or regenerate the mascot. If the read fails, do not publish.
c) Renderer: after cloning the repo in step 7a, copy /home/claude/mygamerfeed-posts/tools/render_bright.py to /home/claude/render_bright.py (do not edit it). Write stories.json as {"date": "WED NOV 4" style uppercase weekday, month and day, "stories": [...]}. Do not set a cover color.
d) Carousel: python3 /home/claude/render_bright.py stories.json /home/claude/out - <point_N.png path> <thumbs_M.png path>

7. HOST ON GITHUB.
a) Call add_repo with owner "philliptmckinney", repo "mygamerfeed-posts", access "push". Clone: git clone --depth 1 https://github.com/philliptmckinney/mygamerfeed-posts /home/claude/mygamerfeed-posts (long timeout, about 10 minutes). Do this before step 6c.
b) Save each slide as JPEG quality 92 in posts/YYYY-MM-DD-HHMM (Central) as slide_01.jpg, slide_02.jpg and so on.
c) Commit with git -c user.name="mygamerfeed" -c user.email="philliptmckinney@users.noreply.github.com" commit -m "Add carousel for YYYY-MM-DD HHMM" plus the trailer lines "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" and the session link line the session gives you, if any. git fetch origin main and rebase before pushing to main.

8. VERIFY (publish only if every check passes).
- Facts: open every source article with WebFetch and confirm every claim on the slides. CONFIRMED needs an official source or two reputable outlets. Drop anything you cannot confirm to its label; if fewer than 3 stories remain, do not publish.
- Independent check: spawn one fresh general-purpose agent with only the stories.json content and the source links, asking it to fact-check every claim and label. Fix or drop anything it flags, then re-render and re-upload.
- Text: no em dashes anywhere, at most 5 hashtags, proper capitalization, correct spelling of every name, today's date on the cover.
- Images: Read every slide; nothing cut off, overlapping or misspelled; slide count is stories plus 2; pointing pose on the cover, thumbs-up on the follow slide.
- Hosting: curl every raw.githubusercontent.com URL (https://raw.githubusercontent.com/philliptmckinney/mygamerfeed-posts/main/posts/<folder>/<file>) for HTTP 200 (retry once after 20 seconds).
If any check fails and cannot be fixed with certainty, publish nothing and write one `alert` document to Gamer Feed HQ (source "Carousel") saying what failed, plus the short notification.

9. DO NOT PUBLISH THROUGH BUFFER (Tyler, Nov 11). TikTok blocked Buffer posts as "potential spam" on Nov 10 and Nov 11, so TikTok is posted by hand from the app until Tyler says otherwise. Never call create_post for TikTok.

10. HAND IT TO TYLER IN HQ (see tasks/INBOX.md). Write one `action` document (source "Carousel"): title "Post today's gaming news carousel on TikTok", body with the ready-to-paste caption, the TikTok title, anything dropped during verification and each story's source link; link = the GitHub folder of today's slides. Then send the short notification. If there was not enough news, write one `info` document saying so instead. Vary the caption's hook and closing line each day; do not reuse the same follow line two days running (repetitive captions are a spam signal).
