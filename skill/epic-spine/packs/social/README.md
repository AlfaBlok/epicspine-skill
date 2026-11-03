# Pack: social

A social campaign desk: personas scan, write, post, reply and measure; the owner (Jordi) steers by a brief, directions, ideas and after-the-fact feedback. **No global approval gate**: a draft that passes its checks is scheduled and posted in its slot; only the owner's own hold rules hold a post (the rule `Kind: post` holds every post: approve-before-posting, below). Opt in: `Pack: social` in the repo's AGENTS.md. Machine-read source: [`schema.json`](schema.json) (this page summarises it; the schema wins).

## Files

| File | One item is | Fields | Written by |
|---|---|---|---|
| brief (`data/brief.md` + sections kept where they live) | the standing brief | objective (root `## Goal`), targets (root `## Targets`), audience, key messages with weight (message house `## Points to emphasize`, as a `# · Message · Weight · Source` table), voice, style rules, never say, topic weights, feedback log (message house), formats mix (format, share, example), examples (link, like/dislike, why), hold for me (R1…, default none) | Jordi; Writer adds style rules + feedback-log lines (C6) |
| directions (`data/directions.md`) | a week highlight, a do/don't, the month's priority | `## Week` H1… (highlight, why, until, served by), `## This week only` (do / don't, rule, until), `## Voice note`, `## Month` M1… (priority, why, month, served by) | Jordi |
| topics (`data/topics.md`) | a finding from today's scan, table replaced daily | rank, T-MMDD-n, topic, where, evidence link, heat, date, reply target, used by | Scout |
| ideas (`data/ideas.md`) | an idea for a post, open across platforms (never expires) | I-n, date, idea, format, platform (the platforms it fits, one or more), from (role), link or asset, state, why, became, used on (computed: its posts by platform) | Jordi and Scout add; the Writer moves state, Jordi may drop (park) one |
| posts (`data/posts-ledger.md`) | one post, reply in a thread, or outreach (never a DM) | P-nnnn, date, persona, kind (post / reply / outreach), platform, campaign (optional), community, slot, title, text, format, assets, topic, highlight, messages, idea, checks, link, replies, metrics, result, feedback, status | Writer, Responder, Engager write rows; Publisher the link; Reporter numbers; Jordi feedback (and text before its slot) |
| messages (`data/messages-ledger.md`, optional) | `## Chats`: one conversation (DM, chat request); `## Messages`: one message in or out | Chats: C-nnnn, platform, account (ours), who, kind (dm / chat request / pm), link, campaign (optional), started, state, reason, feedback, messages (computed). Messages: M-nnnn, chat, at, from (them / us), persona, text (ours in full; theirs one short line verbatim, else `summary: …`), answers, checks, feedback, result, status | Responder (Delivery manager for a migration); Jordi: feedback, text of a draft, Send / Don't send / Undo, a chat's Draft requested / Accept requested / Done |
| insights (`data/insights.md`, optional) | `## Insights`: what is working, from numbers we can read; `## Proposed calls`: a My calls line for a campaign's one-pager | Insights: IN-n, insight, use (one do / avoid line), evidence (post ids + numbers), confidence (low / medium / high · n posts), campaign (optional), since, state (`active`, `retired`). Proposed calls: MC-n, call, evidence (two or more notes), campaign, since, state (`proposed`, `accepted`, `dismissed`) | Reporter (weekly pass + each campaign's last day); Jordi accepts or dismisses a call (Undo back to proposed) |
| threads (`data/threads.md`, optional) | a hot thread in our lane, kept (not replaced daily) | TH-MMDD-n, found, platform, community, title, link, why ours, numbers (as read), visibility, campaign (optional), reply (our outreach row), state (`watch → drafted → sent`, `skipped`, `cooled`) | Scout adds and scores (morning + 16:00 UTC); Engager: reply, drafted / sent / skipped / cooled |
| assets (`data/assets.md` + `data/assets/`) | a diagram, screenshot, clip, video or logo | A-n, kind, file, made by, source, cuts per channel, used by | Jordi; the Writer adds the diagram of its own post (made with the `diagram` skill); the Video Maker adds the clips it renders |
| reports (`data/reports/<date>.md`) | one 3-day report | Numbers, Best and worst, Learned, Highlights covered, Feedback themes, Cost | Reporter |

"Used by", "served by", "carried by" and "became" are computed by the export from post fields; nobody types them.

## Post statuses

`idea → draft → scheduled → posted → measured`, plus `held`, `pulled`, `expired`. `idea` is the ideas.md row; the ledger row is written at `draft`.

| From | To | Who | When |
|---|---|---|---|
| idea | draft | Writer | takes the idea |
| draft | scheduled | Writer | every check passes, no hold rule matches |
| draft | held | Writer | a hold rule matches |
| held | scheduled | Jordi | approves it (the console writes `Approved <date>` in the row's Feedback) |
| held | scheduled | Writer | Jordi approved it with feedback (`Approved with feedback <date>: …` in Feedback): the Writer applies it to the text, then schedules it |
| scheduled | posted | Publisher | its slot; link in the same commit |
| scheduled | expired | Publisher | best-before passed |
| draft | posted | Responder, Engager | reply / outreach rows, checks pass |
| posted | measured | Reporter (any); Responder, Engager (their rows) | 48 h after posting |
| draft, held, scheduled | pulled | Jordi | unscheduled, never goes out |
| posted, measured | pulled | Jordi | the Publisher deletes the live post at once, link kept (C5) |
| pulled | held, scheduled, draft | Jordi | Undo of a pull (restore) on a post that never went out (no Link): back to the status it had before, with its slot; a scheduled post whose slot has passed comes back `held`, for him to post now or give a new slot |

A failed check keeps the draft a draft, with the reason in `checks`.

**Ideas never expire (agent_team E64-S4).** Ideas: `new → open → spent`, or `parked` (why; back to open) or `epic` (too big for one post), all moved by the Writer; Jordi may drop an open idea (`new`, `open`, or legacy `picked up`, `drafted`, `posted` → `parked`, the console's drop). An idea goes `open` with its first post and stays open: the Writer picks an open idea and a platform it has not been used on (`used on`, computed from the posts' Idea and Platform), so one idea becomes a Reddit thread, an X post and later a LinkedIn post, each written fresh; a post's Idea may repeat across rows. It closes only when Jordi parks it or the Writer marks it `spent` (every platform it fits is used, or the angle is stale; Why says which). `picked up`, `drafted` and `posted` are legacy states (read as open; the Writer moves them to `open`); their old moves carry `"legacy": true`: the validator still accepts them, role texts no longer list them.

**Thread replies wait for Jordi (agent_team E64-S6).** An outreach row (a disclosed reply in someone else's thread) matching a hold rule (the brief's `Kind: outreach`) goes `draft → held` by the Engager, never straight to `posted` (check `hold_rules_outreach`); Jordi's Approve moves it `held → scheduled` (his `Approved` note; with feedback the Engager applies it first); the Engager sends it inside the caps (`scheduled → posted`, link in the same commit) or, when it waited more than 12 h on X or 24 h on Reddit, marks it `expired` (cooled), never sent late.

**Campaigns inside a repo (optional `Campaign` column, agent_team E60-S1).** A campaign is a child epic of the social repo (`docs/spines/*.md` with a `## Campaign plan` section: period, platform, key messages, voice, posting and reply style, targets, personas and cadence). A post, reply or outreach row counts toward it when its `Campaign` cell holds the campaign's epic code (e.g. `EPIC-7`); the code never changes when the campaign is renamed. Empty, or a ledger without the column, means the repo itself (no campaign), so older ledgers stay valid as they are. Writer, Responder and Engager set it on the rows they add for a campaign; Jordi may retag a row.

**Approve before posting (opt-in per campaign, agent_team E46-S2).** The pack keeps no global gate; a campaign that wants Jordi to approve every post adds the hold rule `Kind: post` to its brief's Hold for me table (the console's "Approve every post" switch writes it). Every new post then goes `draft → held`; Jordi approves (→ `scheduled`), asks for a change (`Revise requested <date>: …` in Feedback: the Writer makes a new version, keeps it `held` and starts Checks with `Revised <date>`, so it comes back to him for review; it is never scheduled without his `Approved` note), approves with feedback (stays `held` until the Writer applies it and schedules it) or does not post it (→ `pulled`; restore puts a never-posted pulled post back to the status it had before the pull: `held`, or `scheduled` with its slot while that slot is ahead, else `held`). The `approved` check makes `held → scheduled` need Jordi's `Approved` note in Feedback, a column only Jordi writes.

## Messages: DMs wait for Jordi's Send (agent_team E34-S27)

DMs are not posts: they never go to the posts ledger (the hook refuses a new posts row whose Community is `DM …` or `DMs`). Each conversation is a Chats row; each message a Messages row.

| Message status | To | Who | When |
|---|---|---|---|
| (new) | received | Responder | their message, as it came |
| (new) | draft | Responder | our reply, for Jordi's Send |
| draft | scheduled | **Jordi only** | Send: his `Approved <date>` note in Feedback (`send_approved`) |
| draft | pulled | Jordi | Don't send; Undo: pulled → draft |
| scheduled | draft | Jordi | Undo of Send before it went out |
| scheduled | posted | Responder | sends it exactly as written, dry run first; the send in Result (`sent`); Text is frozen once scheduled |
| draft | expired | Responder | they wrote again first; a new draft answers them |

The message lifecycle declares its own `approval_gate: true`, so the pack's "no global gate" stays true for posts. Chat states: `open` (they wrote last), `waiting` (we did), `left` (by rule: Reason + Link, one row per chat, never a bundle), `hidden` (the request text is hidden until accepted; the Responder never accepts on its own), `done`. Jordi's buttons: Draft a reply for me (left → open, `Draft requested`), Accept and draft a reply (hidden → open, `Accept requested`), Done, no reply needed (→ done, Undo back). Moving old DM rows out of the posts ledger: the Delivery manager adds them here and sets the old rows to `moved` (Result `moved to data/messages-ledger.md C-…`), never deletes them; the export skips `moved` rows.

## Who writes what

| Role | Writes | May not |
|---|---|---|
| Jordi (console, digest, desk chat) | brief, directions, ideas (from: Jordi), assets, post feedback, approve held (with or without feedback, or with a new slot when its slot has passed), ask for a new version of a held post (revise), pull any, restore a pulled post that never went out | (nothing waits for him unless a hold rule holds it) |
| Scout | topics; adds ideas; threads (adds, scores, watch / skipped / cooled) | posts |
| Writer | post rows as draft; draft → scheduled / held; held → scheduled once Jordi approved it with feedback and the feedback is applied; a new version of a held post on Jordi's `Revise requested` note (stays held, Checks starts `Revised <date>`); idea state; style rule from 2× feedback (C6, undo = revert); asset rows for its posts' diagrams | schedule a failing draft, release a held post Jordi did not approve, post |
| Publisher | scheduled → posted (link) / expired; deletes pulled live posts | post a draft or held post, change text |
| Responder · Engager | reply / outreach rows: draft → posted → measured; replies, metrics. Engager: outreach draft → held when a hold rule matches, sends it after Jordi's Approve (scheduled → posted) or marks it cooled (expired); threads' Reply and drafted / sent / skipped / cooled. Responder: the messages ledger (chats, their messages, DM drafts; sends only replies Jordi scheduled) | top-level posts; a DM in the posts ledger; send a DM draft |
| Delivery manager | moves rows between pack files (old DM rows → messages ledger; the posts row → `moved`) | any other edit |
| Reporter | posted → measured, metrics, result, reports; insights (lines active / retired) and proposed calls | any other status; accept a call |
| Video Maker | renders clips and registers each in `data/assets.md` (row, made by Video Maker) + `data/assets/<id>/` | posts, ideas, topics, any status |

## Checks (validator, E34-S2)

At `draft → scheduled` / `draft → posted` (the text checks also at `draft → held` and `held → scheduled`): Reddit no link on line 1 and at most one link; disclosure ("I built…") in the first two lines on Reddit for posts and outreach (a reply in our own thread needs none); no Never say phrase; caps (1 thread a day, 1 per community a week, 20 replies a day); hold rules (→ held). At `held → scheduled`: Jordi's `Approved` note in Feedback (`approved`). At `scheduled → posted` / `draft → posted`: the link is in the row. Messages: `send_approved` at `draft → scheduled` (Jordi's `Approved`), `sent` at `→ posted` (Result filled), never-say at Send; checks name the lifecycles they apply to (`lifecycles`). Every status change must be a listed transition by one of its roles (the role is checked when the commit names its writer, `EPICSPINE_PERSONA`). How to run it: [references/packs.md](../../references/packs.md) Validate.

## Desk intake (6 kinds)

What Jordi says in the desk chat is one of six kinds; the desk writes it where the kind says (as Jordi, through the console's write API) and replies with where it landed (file + section link) and undo. Brief change → brief sections (root Goal/Targets, message house, brief.md); Key message → message house Points to emphasize (+ weight); Priority → directions Week / Month / This week only; Idea → ideas.md row (from: Jordi, state new, + assets); Big idea → a new child epic (Delivery manager); Feedback on a post → the post's Feedback + message house Feedback log. Unsure: ask one line back. Source: `schema.json` `intake`; prompt text: `pack.py social --wake-text` (a persona's own: `--role Writer`; [references/packs.md](../../references/packs.md) Desk intake).

## From today's zenod-social (for E34-S4)

Listener → Scout; Author → Writer (+ Publisher). The posts ledger keeps its 8 columns and gains Id, Kind, Community, Slot, Text, Format, Assets, Topic, Highlight, Messages, Idea, Checks, Metrics, Feedback; old status `draft (manual)` and `approved` map to `draft`. Topics gain Id and Heat (+ Reply target). Points to emphasize becomes a table with Weight. brief.md, directions.md, ideas.md, assets.md and reports/ are new.
