# Shared totems: where a team reads and leaves traces

> **Status: proposal** (agent_team EPIC-64 row E64-S11, 2026-11-03). It waits on the owner's answer to agent_team ask E64-A4. The deck is at http://vps3.taild81fbb.ts.net:8971/ (tailnet). Nothing here binds until that ask is answered and this branch is merged.

A team of agents works well when every member reads the same few places when it wakes and writes back to the same places when it is done. It fails quietly when each new feature adds a channel (a file, a table, a message kind), because then a note lands somewhere that nobody is handed at the next wake. These few shared places are the **totems**. There are four, and nothing else is a place to read or write state.

| Totem | Answers | One item is | Who changes it |
|---|---|---|---|
| **Brief** | What do we want? (forward) | a section of intent: goal, why, the bet, audience, voice, measures, the owner's calls, not doing | the owner, or a desk doing exactly what the owner said (with Undo); agents propose through Observations |
| **Observations** | What have we learned? | a dated line with evidence: an owner note, a measured lesson, a proposed brief change; `active` or `retired`, never deleted | anyone, with evidence; the owner accepts a proposed brief change |
| **History** | What did we do? | a tree: level 1 (a week or phase, one sentence), level 2 (a day, one sentence), level 3 (one line per wake, with a link) | each wake adds its level-3 line; a digest role folds days and weeks |
| **Work** | What is next to do? | a ledger row with an assignee and a status | per the ledger's own rules (Issue Ledger, a pack's ledgers) |

## The build team already has them

A spine is the four totems for a build goal. The doctrine only names them and extends them to every kind of team.

| Totem | In a spine | In a pack repo (e.g. social) |
|---|---|---|
| Brief | `## Goal`, `## Done means`, `## Non-Goals` | the pack's brief (world) + each campaign spine's `## Brief` (one `###` section per slide) |
| Observations | `## Operating Learnings` | the pack's observations file |
| History | `## Current State` (Last attempted, Result), `## Decisions`, git log | the pack's history file (week, day, wake lines) |
| Work | `## Issue Ledger` | the pack's ledgers |

## The rules

1. **Read at wake.** Every persona and worker starts from the four totems of its goal and of every ancestor up to the root: the whole brief, the active observations, History level 1 plus everything new since its own last wake, and its own Work rows. The host (console, dispatcher) hands these in the wake text. It never only names a file to go and read. Keep the pack to about one screen. A brief longer than that is a brief to cut.
2. **Leave a trace.** Every wake ends with its Work changes and exactly one History line (`HH:MM <role>: <what it did>, <link>`), in the same commit. A wake that did nothing writes nothing, and the wake gate records it as idle.
3. **The owner's words are filed, never left in a chat.** Every message from the owner (desk chat, a campaign chat, a comment on a brief section, feedback on an item, a voice note) is filed on one totem, scoped to the goal it is about (this campaign, or all), with a History line. The desk's reply links to the exact spot and offers Undo. When the scope is unclear the desk asks one line: "this one or all?". A chat transcript is never a source for any persona.
4. **Only the owner moves the brief.** A desk may write the owner's own words into the brief at once, with Undo. Any other agent proposes a brief change as an Observations line that cites at least two agreeing items of evidence (for example the owner's note and a measured lesson). The owner accepts it or dismisses it.
5. **Observations are retired, never deleted.** A line that a newer line replaces is marked `retired` with the replacing line's id. Personas are handed only `active` lines.
6. **Digests are views.** A daily report, a digest message or a status page is drawn from History (and its detail files). It is never a separate store that another persona must remember to read.
7. **No new channel.** A feature that needs to keep something extends one of the four totems: a new section, column or item kind. Before adding a file, table or message kind, name the totem it extends. If none fits, that is a product question for the owner, not a design choice for the agent.

## The lifecycle of an owner's note

1. The owner says it anywhere: a desk, a campaign chat, a brief section, an item.
2. The desk files it (rule 3): Brief for a change of intent, Observations for a note or a judgement, Work for a new idea or task, a new goal for a big idea.
3. One History line records it. The desk's reply carries the link and Undo.
4. At their next wake, every persona of that goal is handed the changed brief and the note under "new since your last wake" (rule 1).
5. Each persona does its work and leaves its History line (rule 2), which says what it did with the note when it used it.

For a build goal the same path ends in a Work row that the Delivery manager dispatches. For a campaign it ends in the personas' next posts.

## Checks (once built)

- `pack.py validate` refuses a commit that changes Work rows without a History line by the same role in that commit (rule 2).
- The desk's intake text names the totem and the scope of every kind (rule 3).
- The host's wake text for every persona of a pack repo carries the four totems (rule 1). A test asserts that each role's wake text quotes the active brief and the newest owner note.

See also: [packs.md](packs.md) (a pack's files and intake), [spine-model.md](spine-model.md) (the sections every epic has), [learnings.md](learnings.md) (Operating Learnings).
