# Pack: social

A social campaign desk: personas scan, write, post, reply and measure; the owner (Jordi) steers by a brief, directions, ideas and after-the-fact feedback. **No approval gate**: a draft that passes its checks is scheduled and posted in its slot; only the owner's own hold rules hold a post. Opt in: `Pack: social` in the repo's AGENTS.md. Machine-read source: [`schema.json`](schema.json) (this page summarises it; the schema wins).

## Files

| File | One item is | Fields | Written by |
|---|---|---|---|
| brief (`data/brief.md` + sections kept where they live) | the standing brief | objective (root `## Goal`), targets (root `## Targets`), audience, key messages with weight (message house `## Points to emphasize`, as a `# · Message · Weight · Source` table), voice, style rules, never say, topic weights, feedback log (message house), formats mix (format, share, example), examples (link, like/dislike, why), hold for me (R1…, default none) | Jordi; Writer adds style rules + feedback-log lines (C6) |
| directions (`data/directions.md`) | a week highlight, a do/don't, the month's priority | `## Week` H1… (highlight, why, until, served by), `## This week only` (do / don't, rule, until), `## Voice note`, `## Month` M1… (priority, why, month, served by) | Jordi |
| topics (`data/topics.md`) | a finding from today's scan, table replaced daily | rank, T-MMDD-n, topic, where, evidence link, heat, date, reply target, used by | Scout |
| ideas (`data/ideas.md`) | an idea for a post | I-n, date, idea, format, platform, from (role), link or asset, state, why, became | Jordi and Scout add; only the Writer moves state |
| posts (`data/posts-ledger.md`) | one post, reply or outreach | P-nnnn, date, persona, kind (post / reply / outreach), platform, community, slot, title, text, format, assets, topic, highlight, messages, idea, checks, link, replies, metrics, result, feedback, status | Writer, Responder, Engager write rows; Publisher the link; Reporter numbers; Jordi feedback (and text before its slot) |
| assets (`data/assets.md` + `data/assets/`) | a diagram, screenshot, clip, video or logo | A-n, kind, file, made by, source, cuts per channel, used by | Jordi (Video Maker once it exists) |
| reports (`data/reports/<date>.md`) | one 3-day report | Numbers, Best and worst, Learned, Highlights covered, Feedback themes, Cost | Reporter |

"Used by", "served by", "carried by" and "became" are computed by the export from post fields; nobody types them.

## Post statuses

`idea → draft → scheduled → posted → measured`, plus `held`, `pulled`, `expired`. `idea` is the ideas.md row; the ledger row is written at `draft`.

| From | To | Who | When |
|---|---|---|---|
| idea | draft | Writer | takes the idea |
| draft | scheduled | Writer | every check passes, no hold rule matches |
| draft | held | Writer | a hold rule matches |
| held | scheduled | Jordi | releases it |
| scheduled | posted | Publisher | its slot; link in the same commit |
| scheduled | expired | Publisher | best-before passed |
| draft | posted | Responder, Engager | reply / outreach rows, checks pass |
| posted | measured | Reporter (any); Responder, Engager (their rows) | 48 h after posting |
| draft, held, scheduled | pulled | Jordi | unscheduled, never goes out |
| posted, measured | pulled | Jordi | the Publisher deletes the live post at once, link kept (C5) |

A failed check keeps the draft a draft, with the reason in `checks`. Ideas: `new → picked up → drafted → posted`, or `parked` (why; back to picked up) or `epic` (too big for one post), all moved by the Writer.

## Who writes what

| Role | Writes | May not |
|---|---|---|
| Jordi (console, digest, desk chat) | brief, directions, ideas (from: Jordi), assets, post feedback, release held, pull any | (nothing waits for him) |
| Scout | topics; adds ideas | posts |
| Writer | post rows as draft; draft → scheduled / held; idea state; style rule from 2× feedback (C6, undo = revert) | schedule a failing draft, release held, post |
| Publisher | scheduled → posted (link) / expired; deletes pulled live posts | post a draft or held post, change text |
| Responder · Engager | reply / outreach rows: draft → posted → measured; replies, metrics | top-level posts |
| Reporter | posted → measured, metrics, result, reports | any other status |

## Checks (validator, E34-S2)

At `draft → scheduled` / `draft → posted`: Reddit no link on line 1 and at most one link; disclosure ("I built…") in the first two lines on Reddit for posts and outreach (a reply in our own thread needs none); no Never say phrase; caps (1 thread a day, 1 per community a week, 20 replies a day); hold rules (→ held). At `scheduled → posted` / `draft → posted`: the link is in the row. Every status change must be a listed transition by one of its roles (the role is checked when the commit names its writer, `EPICSPINE_PERSONA`). How to run it: [references/packs.md](../../references/packs.md) Validate.

## From today's zenod-social (for E34-S4)

Listener → Scout; Author → Writer (+ Publisher). The posts ledger keeps its 8 columns and gains Id, Kind, Community, Slot, Text, Format, Assets, Topic, Highlight, Messages, Idea, Checks, Metrics, Feedback; old status `draft (manual)` and `approved` map to `draft`. Topics gain Id and Heat (+ Reply target). Points to emphasize becomes a table with Weight. brief.md, directions.md, ideas.md, assets.md and reports/ are new.
