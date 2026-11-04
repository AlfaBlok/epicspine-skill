# Pack: social

A social campaign desk: personas scan, write, post, reply and measure; the owner (Jordi) steers by a brief, directions, ideas and after-the-fact feedback. **No global approval gate**: a draft that passes its checks is scheduled and posted in its slot; only the owner's own hold rules hold a post (the rule `Kind: post` holds every post: approve-before-posting, below). Opt in: `Pack: social` in the repo's AGENTS.md. Machine-read source: [`schema.json`](schema.json) (this page summarises it; the schema wins).

## Files

| File | One item is | Fields | Written by |
|---|---|---|---|
| brief (`data/brief.md`, objective and targets in the root spine) | the standing brief | objective (root `## Goal`), targets (root `## Targets`), audience, key messages with weight (`## Points to emphasize`, as a `# · Message · Weight · Source` table), voice, style rules, never say, topic weights, feedback log, formats mix (format, share, example), examples (link, like/dislike, why), hold for me (R1…, default none) | Jordi; Writer adds style rules + feedback-log lines (C6) |
| directions (the `This week` part of `data/brief.md`; was `data/directions.md`) | a week highlight, a do/don't, the month's priority | `## Week` H1… (highlight, why, until, served by), `## This week only` (do / don't, rule, until), `## Voice note`, `## Month` M1… (priority, why, month, served by) | Jordi |
| topics (`data/topics.md`) | a finding from today's scan, table replaced daily | rank, T-MMDD-n, topic, where, evidence link, heat, date, reply target, used by | Scout |
| ideas (`data/ideas.md`) | an idea for a post, open across platforms (never expires) | I-n, date, idea, format, platform (the platforms it fits, one or more), from (role), link or asset, state, why, became, used on (computed: its posts by platform) | Jordi and Scout add; the Writer moves state, Jordi may drop (park) one |
| posts (`data/posts-ledger.md`) | one post, reply in a thread, or outreach (never a DM) | P-nnnn, date, persona, kind (post / reply / outreach), platform, campaign (optional), community, slot, title, text, format, assets, topic, highlight, messages, idea, checks, link, replies, metrics, result, feedback, status | Writer, Responder, Engager write rows; Publisher the link; Reporter numbers; Jordi feedback (and text before its slot) |
| messages (`data/messages-ledger.md`, optional) | `## Chats`: one conversation (DM, chat request); `## Messages`: one message in or out | Chats: C-nnnn, platform, account (ours), who, kind (dm / chat request / pm), link, campaign (optional), started, state, reason, feedback, messages (computed). Messages: M-nnnn, chat, at, from (them / us), persona, text (ours in full; theirs one short line verbatim, else `summary: …`), answers, checks, feedback, result, status | Responder (Delivery manager for a migration); Jordi: feedback, text of a draft, Send / Don't send / Undo, a chat's Draft requested / Accept requested / Done |
| insights (`data/insights.md`, optional, **retired** by agent_team E64-S14) | kept read-only as evidence in repos that have it; nobody writes it | the Reporter's lessons are `L-<n>` lines in the epic's `## Operating Learnings` (source and evidence, `retired by L-<m>` when replaced) and a brief change it proposes ends its learning line with `proposed for the brief (<part>): "<line>"` (two agreeing items); Jordi adds it or says not now on the campaign's Observations tab | Reporter (weekly pass + each campaign's last day) |
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
| scheduled | held | Publisher | its slot passed over 60 min ago and Jordi has not released it since (his `Approved` or `Post now` note dated at or after the slot): a late post never goes out, it waits for Jordi (rule `no_late_post`, agent_team E60-S2) |
| draft | posted | Responder, Engager | reply / outreach rows, checks pass |
| posted | measured | Reporter (any); Responder, Engager (their rows) | 48 h after posting |
| draft, held, scheduled | pulled | Jordi | unscheduled, never goes out |
| scheduled | held | Jordi | Restore of a retired campaign: its posts whose slot passed while it was retired come back held, for him to post now or give a new slot (agent_team E60-S2) |
| posted, measured | pulled | Jordi | the Publisher deletes the live post at once, link kept (C5) |
| pulled | held, scheduled, draft | Jordi | Undo of a pull (restore) on a post that never went out (no Link): back to the status it had before, with its slot; a scheduled post whose slot has passed comes back `held`, for him to post now or give a new slot |

A failed check keeps the draft a draft, with the reason in `checks`.

**Ideas never expire (agent_team E64-S4).** Ideas: `new → open → spent`, or `parked` (why; back to open) or `epic` (too big for one post), all moved by the Writer; Jordi may drop an open idea (`new`, `open`, or legacy `picked up`, `drafted`, `posted` → `parked`, the console's drop). An idea dropped for good goes `rejected` (from `new`, `open` or `parked`, by Jordi or the Writer recording his drop): the pile of what we dropped, its Why keeping the lesson and who dropped it; only Jordi takes it back to `open`. An idea goes `open` with its first post and stays open: the Writer picks an open idea and a platform it has not been used on (`used on`, computed from the posts' Idea and Platform), so one idea becomes a Reddit thread, an X post and later a LinkedIn post, each written fresh; a post's Idea may repeat across rows. It closes only when Jordi parks it or the Writer marks it `spent` (every platform it fits is used, or the angle is stale; Why says which). `picked up`, `drafted` and `posted` are legacy states (read as open; the Writer moves them to `open`); their old moves carry `"legacy": true`: the validator still accepts them, role texts no longer list them.

**Thread replies wait for Jordi (agent_team E64-S6).** An outreach row (a disclosed reply in someone else's thread) matching a hold rule (the brief's `Kind: outreach`) goes `draft → held` by the Engager, never straight to `posted` (check `hold_rules_outreach`); Jordi's Approve moves it `held → scheduled` (his `Approved` note; with feedback the Engager applies it first); the Engager sends it inside the caps (`scheduled → posted`, link in the same commit) or, when it waited more than 12 h on X or 24 h on Reddit, marks it `expired` (cooled), never sent late.

**Campaigns inside a repo (optional `Campaign` column, agent_team E60-S1).** A campaign is a child epic of the social repo (`docs/spines/*.md` with a `## Campaign plan` section: period, platform, key messages, voice, format, posting and reply style, cadence per channel, reader action, targets, personas and cadence). Its brief is six set parts in the owner's words (agent_team E60-S6): topics (`### Key messages`), voice (`### Voice`), format (`### Format`: text only, text + images, video, or a mix), channels (the `Platform:` line, one or several), cadence per channel (`### Cadence per channel`, one line per channel) and the reader action (`### Reader action`); every persona wake on the campaign starts from them (rule `campaign_tag`), and the console says whether the campaign is live (posting) or not, derived from its Publisher and period, never typed. A post, reply or outreach row counts toward it when its `Campaign` cell holds the campaign's epic code (e.g. `EPIC-7`); the code never changes when the campaign is renamed. Empty, or a ledger without the column, means the repo itself (no campaign), so older ledgers stay valid as they are. Writer, Responder and Engager set it on the rows they add for a campaign; Jordi may retag a row.

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
| Publisher | only its own campaign's rows (`own_campaign_posts`: its campaign's code in Campaign; on the repo's root spine, rows with no Campaign plus those of a live campaign with no Publisher of its own; never a retired campaign's): scheduled → posted (link) / expired; scheduled → held when its slot passed over 60 min ago and Jordi has not released it since (`no_late_post`); deletes pulled live posts | post a draft or held post, post late, change text, touch another campaign's or a retired campaign's rows |
| Responder · Engager | reply / outreach rows: draft → posted → measured; replies, metrics. Engager: outreach draft → held when a hold rule matches, sends it after Jordi's Approve (scheduled → posted) or marks it cooled (expired); threads' Reply and drafted / sent / skipped / cooled. Responder: the messages ledger (chats, their messages, DM drafts; sends only replies Jordi scheduled) | top-level posts; a DM in the posts ledger; send a DM draft |
| Delivery manager | moves rows between pack files (old DM rows → messages ledger; the posts row → `moved`) | any other edit |
| Reporter | posted → measured, metrics, result, reports; lessons as Operating Learnings lines and proposed brief changes on them (data/insights.md retired, E64-S14) | any other status; accept a proposal |
| Video Maker | renders clips and registers each in `data/assets.md` (row, made by Video Maker) + `data/assets/<id>/` | posts, ideas, topics, any status |

## Checks (validator, E34-S2)

At `draft → scheduled` / `draft → posted` (the text checks also at `draft → held` and `held → scheduled`): Reddit no link on line 1 and at most one link; disclosure ("I built…") in the first two lines on Reddit for posts and outreach (a reply in our own thread needs none); no Never say phrase; caps (1 thread a day, 1 per community a week, 20 replies a day); hold rules (→ held). At `held → scheduled`: Jordi's `Approved` note in Feedback (`approved`). At `scheduled → posted` / `draft → posted`: the link is in the row. Messages: `send_approved` at `draft → scheduled` (Jordi's `Approved`), `sent` at `→ posted` (Result filled), never-say at Send; checks name the lifecycles they apply to (`lifecycles`). Every status change must be a listed transition by one of its roles (the role is checked when the commit names its writer, `EPICSPINE_PERSONA`). How to run it: [references/packs.md](../../references/packs.md) Validate.

## Desk intake (6 kinds)

What Jordi says in the desk chat is one of six kinds; the desk writes it where the kind says (as Jordi, through the console's write API) and replies with where it landed (file + section link) and undo. Brief change → brief sections (root Goal/Targets, brief.md); Key message → brief.md Points to emphasize (+ weight); Priority → brief.md Week / Month / This week only; Idea → ideas.md row (from: Jordi, state new, + assets); Big idea → a new child epic (Delivery manager); Feedback on a post → the post's Feedback + message house Feedback log. Unsure: ask one line back. Source: `schema.json` `intake`; prompt text: `pack.py social --wake-text` (a persona's own: `--role Writer`; [references/packs.md](../../references/packs.md) Desk intake).

## Shared totems (agent_team E64-S11, approved under E64-A5 2026-11-03)

Every campaign is an EpicSpine child epic of the repo's root spine, and the four totems of [references/totems.md](../../references/totems.md) are four parts of its spine file. The approved shape (scripts and checks follow in agent_team E64-S12..S14).

**Done in agent_team E64-S13 (skill 2026.11.03.7):** the message house and directions are folded into `data/brief.md` (the schema's `brief.*` and `directions.*` sections all live there now, headings unchanged; `schema.json` `folded` names the old files, and `pack.py` export and validate warn about a repo still holding one, never failing a commit for it). The `## Feedback log` table stays in `data/brief.md` as the log of Jordi's feedback on posts the console writes; each note is also filed as an Operating Learning of the epic it is about.

The approved shape:

| Totem | Root spine (the whole team) | Campaign spine | Folds in today's |
|---|---|---|---|
| Brief | `## Goal`, `## Targets`; `data/brief.md` (positioning, key messages with weight, voice, never say, topic weights, style rules, formats, hold for me, `## This week`) is the root brief's body | `## Goal`, `## Done means` (standing: `## Targets`), `## Campaign plan` with one `###` per slide (Why this campaign, The bet, Who and where, How we sound, What we measure and hope, My calls and not doing), `## Non-Goals`; slide 1 "Where we are" is drawn from Goal and Current State | `data/message-house.md` (all but Feedback log and Learnings) and `data/directions.md` into `data/brief.md`; the one-pager draft into the slides; the campaign deck files and their servers (the console draws the deck) |
| Observations | `## Operating Learnings` (true everywhere) | `## Operating Learnings`: `L-<n> \| source (Jordi, Reporter) \| line \| evidence \| date`, retired lines kept | message house `## Feedback log` and `## Learnings`; `data/insights.md` IN-n lines become learnings, MC-n proposed calls become proposed brief changes |
| History | `## Decisions`, `## Weeks` | `## Decisions`, `## Weeks` (one line per week: result against its Done means or Targets, link to `docs/log/<campaign>/<yyyy-Www>.md` with day lines and one line per wake) | the Reporter's daily report summary (the report file stays as the day's detail), the digest message (drawn from it), `data/onboarding-log.md` |
| Work | `## Issue Ledger` (cross-campaign tasks) | `## Issue Ledger`: task rows (research, a logo, a thread to answer, a post to write), each with an owner, a status and an outcome linking its result (P-id, note, A-id) | nothing moves: `data/posts-ledger.md`, `ideas.md`, `threads.md`, `messages-ledger.md`, `assets.md` stay the team's queues, tagged by campaign; `data/topics.md` rows kept go to threads or ideas, the rest is the Scout's scratch |

**Kinds.** An ongoing campaign (e.g. X awareness) is `Spine kind: standing`: weekly `## Targets`, a `Scoreboard:` line, never `done`; a missed target is a task row. A campaign with an end (a one-week push, recruiting N testers) is an ordinary epic that closes with its `## Outcome`.

**Who picks up a task.** The campaign's Delivery manager gives each new row an owner at its next wake: Scout (research, threads to watch), Writer (posts, held for Jordi), Engager (replies in others' threads), Responder (replies on ours, DMs), Reporter (measurements), Publisher (posting a scheduled row); a task no role fits (a logo, a video, a page) goes to a ticket worker, as in a build epic. Daily rounds stay the plan's `### Personas and cadence`, not rows. A row whose outcome needs Jordi goes to `review` with its card and shows on his Team home and first on the campaign's Work tab.

**Desk intake, pointed at the epic.** Brief change, Key message, Priority → the Brief of the campaign the note is about (its slide, rebuilt with Undo), or the root's when it is about all (ask "this campaign or all?" when unclear), plus an Operating Learning with Jordi's words. A judgement → an Operating Learning. A thing to do (research, make, write, answer) → a task row. Feedback on a post → the post's Feedback; repeated, an Operating Learning. Idea → `data/ideas.md`. Big idea → a new campaign epic (Delivery manager). A yes or no → a Decision. Every reply names where it landed and links there.

**Wake text.** Every role (Scout, Writer, Responder, Engager, Reporter; the Publisher for its due posts only) is handed the same pack at the top of its wake: the root's and the campaign's brief, the learnings in force, the week lines plus History since its last wake, and its own task rows. The Writer brief of E64-S4 becomes this pack plus its ideas pool and posted history.

**Who writes what, added.** Every role: its rows' status and outcome, one History line per wake. Reporter: learnings with evidence, proposed brief changes, day lines and the week's line against its targets. Desk and campaign chat (as Jordi): Brief, learnings with his words, task rows, Decisions. Delivery manager: owners for new rows. Jordi: everything in the Brief; accept or dismiss a proposed change; approve a task in review.

## From today's zenod-social (for E34-S4)

Listener → Scout; Author → Writer (+ Publisher). The posts ledger keeps its 8 columns and gains Id, Kind, Community, Slot, Text, Format, Assets, Topic, Highlight, Messages, Idea, Checks, Metrics, Feedback; old status `draft (manual)` and `approved` map to `draft`. Topics gain Id and Heat (+ Reply target). Points to emphasize becomes a table with Weight. brief.md, directions.md, ideas.md, assets.md and reports/ are new.
