# Reporting to Gamer Feed HQ (applies to every @mygamerfeed task)

Tyler wants ONE place to keep up with @mygamerfeed (Nov 11): the Gamer Feed HQ page,
https://claude.ai/artifact/UHDe6R9SQzYbUuSRmTNkig . Every task reports there. This replaces any
"send Tyler a message" step in the task file, except where the task file says to also send a short
message.

## How to report

Load `ArtifactData` with ToolSearch. Write one document to collection `inbox` on that url with
action `set`, a NEW doc_id `<task-slug>-<YYYYMMDD-HHMM>` (Central time, letters, digits and dashes only),
and no `if_version` (it is a new document):

    {
      "kind":   "info" | "action" | "alert" | "comments",
      "source": "<the task's short name, e.g. Morning report>",
      "title":  "<one plain line>",
      "body":   "<plain text, short, newlines allowed; no markdown tables>",
      "link":   "<optional https link>",
      "created": "<current UTC time, ISO 8601, e.g. 2026-11-11T14:50:00Z>",
      "done":   false
    }

- `alert`: something broke or failed (a post did not go live, a fact went stale, a step failed).
- `action`: Tyler has to do something (record, approve, choose, review).
- `info`: a result he can read when he wants. Most runs are info.
- `comments`: comment reply drafts (only the comment sweep uses this; see tasks/comments.md).

Write in proper capitalization and full sentences, no em dashes, short enough to read on a phone.
If a run had nothing worth saying (for example a post check where everything went live), write
nothing at all.

## Notifications

Only for `alert`, `action` or `comments` documents, also send ONE short SendUserMessage so his phone
buzzes: the title plus "Details are in Gamer Feed HQ." Never send a message for `info`, except the
morning report, which sends its one-line headline.

## Don't duplicate

Before writing an `action` or `alert`, list the newest 30 inbox documents (query order_by created desc,
limit 30). If an open one (done false) already says the same thing, do not add another.

If the inbox write fails, fall back to one SendUserMessage with the same content.
