Check that Tyler's @mygamerfeed posts actually went live. Tyler said "We can't miss stuff like this" after TikTok blocked two Buffer posts as spam on Nov 10 and nobody caught it for hours. Read-only: never retry, re-send, edit, delete or reschedule any post. Since Nov 11, TikTok is posted by Tyler by hand, so TikTok posts sitting in Buffer as drafts are expected: ignore them.

1. Get the current time with current_time (America/Chicago).
2. Load the Buffer tools with ToolSearch. Organization 6adfbc17399e3947f020b7bc. Channels: TikTok 6adfbda12f1f5ed648def0a3, Instagram 6adfbd4e2f1f5ed648deee80, YouTube 6ae4b9362f1f5ed64821a744. list_posts with dueAt from 90 minutes ago to now, first 20.
3. For each post due in that window:
   - status "sent": fine.
   - status "error": read the error message. TikTok carousels with "media delays" usually post anyway, so check before reporting. For any TikTok error, load the built-in-browser skill and the mcp__remote-devices__Claude_Browser__* tools, open https://www.tiktok.com/tiktokstudio/content, wait 6 seconds, and check document.body.innerText for the post's caption. If it is there, it went live: note it and do not alert. For YouTube, check https://studio.youtube.com/channel/UCjffkzsuHCKMH4Z4LXKBvqg/videos/short with Claude in Chrome if reachable.
   - still "scheduled" or "sending" more than 20 minutes after its dueAt: treat as a failure.
4. If anything failed to go live, write one `alert` document to Gamer Feed HQ (source "Post check"; see tasks/INBOX.md) with: which post, which platform, the exact Buffer error, and the fix (for "potential spam" on TikTok: post it directly from the TikTok app and check TikTok Studio > More tools > Account check; offer to send him the video file and caption). Proper capitalization, no em dashes.
5. If everything went live, write nothing to HQ for this part.

6. QUEUE TOP-UP (this replaces the separate top-up task). Then do the following. Where it says to message Tyler, write an `alert` document to Gamer Feed HQ instead (source "Post check").
 Buffer's free plan allows only 10 scheduled posts per channel, so approved posts that don't fit wait in an overflow file until slots free up.

IMPORTANT (Nov 8): never retry or re-send a TikTok post that Buffer shows as "error" with "media delays". Those carousels actually posted on TikTok anyway, and retrying created duplicates. Leave errored posts alone.

1. Clone the repo: git clone https://github.com/philliptmckinney/mygamerfeed-posts /home/claude/mygamerfeed-posts (call add_repo owner philliptmckinney repo mygamerfeed-posts with access push first if the clone or push is refused). Read queue/README.md and queue/pending.json.
2. If no item in pending.json has status "pending", end quietly with a one-line note.
3. Get the current time with current_time. Load the Buffer tools with ToolSearch. Organization 6adfbc17399e3947f020b7bc. Channels: TikTok 6adfbda12f1f5ed648def0a3, Instagram 6adfbd4e2f1f5ed648deee80, YouTube 6ae4b9362f1f5ed64821a744. For each channel, count scheduled posts (list_posts status scheduled, channelIds that channel, first 50).
4. For each channel with fewer than 10 scheduled posts, take its pending items with the earliest dueAt first and create them with create_post: channelId, schedulingType automatic, mode customScheduled, dueAt as given, text exactly as given, assets [{"video": {"url": <video>}}], and metadata from the item if present (YouTube needs metadata.youtube {title, categoryId "20"}; Instagram needs metadata.instagram {type "reel", shouldShareToFeed true}). Check the video URL returns HTTP 200 first. If an item's dueAt is in the past or under 30 minutes away, schedule it 45 minutes from now instead and note the new time. Stop at 10 per channel.
5. For each item created, set its status to "scheduled" and add "bufferId" and, if moved, "postedAt". Commit "Queue top-up" with the line "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" at the end of the message, and push.
6. Never add, change or invent posts beyond what pending.json lists; never delete or edit existing Buffer posts. Only message Tyler (one short SendUserMessage) if an item had to be moved to a later time, a video URL failed, or Buffer returned an error on a post you created. Otherwise end quietly.
