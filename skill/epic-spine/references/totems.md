# Shared totems: the four parts of every epic a team reads and leaves traces in

> **Status: proposal, round 2** (agent_team EPIC-64 row E64-S11, 2026-11-03). It waits on the owner's answer to agent_team ask E64-A5 (round 1 was E64-A4: the owner asked "are we not using epics? … everything should land in an epic file" and "we also need tasks"). The deck is at http://vps3.taild81fbb.ts.net:8971/ (tailnet). Nothing here binds until that ask is answered and this branch is merged.

A team of agents works well when every member reads the same few places when it wakes and writes back to the same places when it is done. It fails quietly when each new feature adds a channel (a file, a table, a message kind), because then a note lands somewhere that nobody is handed at the next wake.

Those places already exist: they are the sections of an **epic**. Every kind of team (build, social, any pack) keeps its goals as a tree of epics, root → goals (a campaign is one) → tasks (Issue Ledger rows), and every epic has the same four **totems**. Nothing else is a place to read or write state. A pack's `data/` ledgers (posts, ideas, threads, messages) are queues the tasks work through, not a fifth place.

| Totem | Answers | Sections of the epic | One item is | Who changes it |
|---|---|---|---|---|
| **Brief** | What do we want? | `## Goal`, `## Done means` (a standing epic: `## Targets`), the plan (a campaign: `## Campaign plan`), `## Non-Goals`; Current State's first lines are its opening summary | a section of intent | the owner, or a desk doing exactly what the owner said (with Undo); agents propose through Observations |
| **Observations** | What have we learned? | `## Operating Learnings` | one numbered line `L-<n>` with its source (owner note or measured lesson) and evidence; `retired` lines are kept | anyone, with evidence; adding one to the Brief is the owner's Decision |
| **History** | What happened? | `## Decisions`, Current State's Last attempted, and for a standing or ongoing epic `## Weeks` (one line per period with its result against Targets, linking that period's log page: days, then one line per wake), git log | a decision, a week line, a wake line | each wake adds its wake line; the digest role writes the day lines and closes the week; the owner and the desk write Decisions |
| **Work** | What is next to do? | `## Issue Ledger` | a **task** row: id, owner, status, outcome (Latest Evidence) | the Delivery manager assigns; the owner of the row moves it |

A campaign is an ordinary child epic (it closes with an `## Outcome`, e.g. a one-week push or "recruit 10 testers") or, when it is ongoing, a **standing** child epic (`Spine kind: standing`, [standing-spines.md](standing-spines.md)): weekly `## Targets`, a `Scoreboard:` line, never `done`. Both keep the core motion of every epic: an instruction in the file (a task row or the brief) → a persona or worker acts → the outcome is written back (row status and outcome, one History line) for the next wake.

## Tasks

Any one-off job is a task row in the epic it serves: research, a logo, a thread to answer, a post to write, a slide to rebuild. The row names an owner (a persona whose job it is; a ticket worker when none fits, as in a build epic), a status and, when finished, its outcome with a link (the post id, the research note, the asset). A task that grows into a goal of its own becomes a child epic. The recurring rhythm of a role (a daily scan, an hourly reply check) is the plan's cadence, not rows; it leaves its wake lines in History. A missed target becomes a task row ([standing-spines.md](standing-spines.md)).

## The rules

1. **Read the whole epic at wake.** Every persona and worker starts from the four totems of its epic and of every ancestor up to the root: the whole brief, the Operating Learnings in force, the week lines plus everything new in History since its own last wake, and its own task rows. The host (console, dispatcher) hands these in the wake text; it never only names a file. Keep it to about one screen: a brief longer than that is a brief to cut.
2. **Leave a trace.** Every wake ends with its task rows' status and outcome and exactly one History line (`HH:MM <role>: <what it did>, <link>`), in the same commit. A wake that did nothing writes nothing, and the wake gate records it as idle.
3. **The owner's words are filed in the epic, never left in a chat.** Every message from the owner (desk chat, a campaign chat, a comment on a brief slide, feedback on an item, a voice note) lands in one totem of the epic it is about, or of the root when it is about all: a change of intent → the Brief (the slide it is about, rebuilt with Undo) plus an Operating Learning with the owner's words; a judgement → an Operating Learning; a thing to do → a task row; a yes or no → a Decision; a new big idea → a new child epic. The reply names where it landed and links there. When the scope is unclear the desk asks one line: "this one or all?". A chat transcript is never a source for any persona.
4. **Only the owner moves the brief.** A desk may write the owner's own words into the brief at once, with Undo. Any other agent proposes a brief change from Observations, citing at least two agreeing items of evidence (for example the owner's note and a measured lesson); the owner accepts it (a Decision) or dismisses it.
5. **Observations are retired, never deleted.** A line that a newer line replaces is marked `retired` with the replacing line's id. Personas are handed only lines in force.
6. **Digests are views.** A daily report, a digest message or a status page is drawn from History and its log pages. It is never a separate store another persona must remember to read.
7. **No new channel.** A feature that needs to keep something extends one of the four totems of the epic: a section, a column, an item kind. Before adding a file, table or message kind, name the totem it extends. If none fits, that is a product question for the owner, not a design choice for the agent.

## The lifecycle of an owner's note

1. The owner says it anywhere: a desk, a campaign chat, the brief deck (a slide note, or the feedback chat inside the full-screen deck), an item.
2. The desk files it in the epic (rule 3) and adds a Decision or History line. Its reply carries the link and Undo.
3. A task row gets its owner at the Delivery manager's next wake.
4. At their next wake, every persona of that epic and its children is handed the changed brief, the new learning and its own rows (rule 1).
5. Each does its work and leaves its row outcome and History line (rule 2). A row whose outcome needs the owner's eye goes to `review` and shows on the owner's home as a card.

## How the console shows it

One page per epic with a small fixed set of tabs, the same for every team: **Brief** (the brief as a deck: one slide per section, a note on a slide rebuilds it, a full-screen mode with the feedback chat beside the slide), **Work** (task rows, waiting-on-you first, the goal path above; a pack's queues are a second view, e.g. the social Pipeline), **Observations**, **History** (weeks → days → wake lines, Decisions marked), **Chat** (feedback on the whole epic; every reply shows where it landed). Settings and personas sit behind one header button, not tabs.

## Checks (once built)

- `pack.py validate` refuses a commit that changes task rows without a History line by the same role in that commit (rule 2).
- The desk's intake text names the totem and the scope of every kind (rule 3).
- The host's wake text for every persona carries the four totems of its epic and its ancestors (rule 1). A test asserts that each role's wake text quotes the active brief, the newest owner learning and its own task rows.
- `validate_spine.py` accepts `## Weeks` on a standing epic and requires each line to link its log page.

See also: [spine-model.md](spine-model.md) (the sections every epic has), [standing-spines.md](standing-spines.md) (ongoing epics), [learnings.md](learnings.md) (Operating Learnings), [packs.md](packs.md) (a pack's queues and intake).
