# Buffer overflow queue

Buffer's free plan allows 10 scheduled posts per channel. Approved, QA-passed posts that don't fit yet wait here.
The "Buffer queue top-up" scheduled task reads pending.json, and for each channel with free slots creates the
pending posts (earliest dueAt first) with mode customScheduled, schedulingType automatic, then sets status to
"scheduled" with the Buffer post id and commits. YouTube posts carry metadata.youtube {title, categoryId "20"};
Instagram posts carry metadata.instagram {type "reel", shouldShareToFeed true}.
If a pending post's dueAt has passed or is under 30 minutes away, it schedules it at the next free slot that day
instead and notes the new time. Only items in this file are posted: nothing gets added here without Tyler's approval.
