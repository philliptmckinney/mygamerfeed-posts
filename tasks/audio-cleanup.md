Clean up old voiceover audio for Tyler's @mygamerfeed page on his Mac. Tyler asked for audio files to go a week after their reels have run, so they don't pile up.

1. Get the current date (current_time, America/Chicago).
2. Read ~/mygamerfeed/Audio/_trash_schedule.json with device_bash (it is at $HOME/mnt/mygamerfeed/Audio/_trash_schedule.json). Each entry under "trash_after" maps a path (relative to ~/mygamerfeed/Audio) to a date.
3. Before moving anything, check Buffer (organization 6adfbc17399e3947f020b7bc, list_posts status scheduled) that no still-scheduled post depends on a reel whose audio is in the list; reels are hosted on GitHub, so normally nothing depends on the audio. If unsure about a file, skip it and note it.
4. For every entry whose date is today or earlier and whose path exists, move it to the macOS Trash with the Control_your_Mac osascript tool: tell application "Finder" to delete POSIX file "/Users/tylermckinney/mygamerfeed/Audio/<path>". This is a move to the Trash, never a permanent delete; never empty the Trash and never use rm. Never touch the "Zelda Story" folder, the _trash_schedule.json file, or anything not listed.
5. Remove the moved entries from _trash_schedule.json (rewrite it with python3 in device_bash, keeping the note).
6. If anything moved, write one `info` document to Gamer Feed HQ (source "Audio cleanup", see tasks/INBOX.md): how many files and how much space went to the Trash. If nothing was due, write nothing.
