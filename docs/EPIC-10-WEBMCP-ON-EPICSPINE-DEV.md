# EPIC-10: WebMCP on epicspine.dev: agents in Chrome can fetch the install command

Spine profile: compact
Repository: AlfaBlok/epicspine-skill
Primary document: docs/EPIC-10-WEBMCP-ON-EPICSPINE-DEV.md
Spine ID: webmcp-on-epicspine-dev-agents-in-chrome-can-fetch-the-install-command
Root spine: [EPIC-0: EpicSpine operating system](EPIC-0-OPERATING-SYSTEM.md)
Parent spine: [EPIC-0: EpicSpine operating system](EPIC-0-OPERATING-SYSTEM.md)
Additional root rationale: n/a
Integration branch: main
Integration policy: main-direct

## Goal

An AI agent running in a visitor's Chrome can ask epicspine.dev for the EpicSpine install command and a summary of each section, through WebMCP tools (`document.modelContext.registerTool`), without scraping the page. Browsers without WebMCP see no change.

## Serves

[EPIC-0: EpicSpine operating system](EPIC-0-OPERATING-SYSTEM.md): makes the public front door usable by browser agents, so an agent can install EpicSpine for its user.

## Done means

- [ ] E10-1 epicspine.dev registers read-only WebMCP tools (install command, section list/summary, jump to section) when `document.modelContext` exists; verified with Chrome's WebMCP testing flag or a stubbed modelContext test.
- [ ] E10-2 Without WebMCP the page behaves exactly as before (no console errors; existing tests pass).
- [ ] E10-3 Visitors' Chrome sees the tools without a flag: origin-trial token for epicspine.dev in a meta tag (needs Jordi to register the trial, E10-A1).

## Current State

Owner: Delivery manager
Status: active
Last attempted: 2026-11-02 E10-S1 dispatched to seat7 (WebMCP tools in index.html on wt/e10-s1-webmcp)
Result: worker running
Evidence: EPIC-0-OPERATING-SYSTEM.md
Waiting on: Jordi: E10-A1 (S1 does not wait on it)
Approved work: readied by Jordi 2026-11-02 ("do epicspine and zenod dev")
Next action: worker builds and tests the tools on a branch; Delivery manager verifies and integrates
Source revision: uncommitted scaffold
Verified at: 2026-11-02

## Waiting on

- [answered E10-A1 2026-11-02 @Jordi] Register epicspine.dev for Chrome's WebMCP origin trial and give us the token — context: Chrome only shows WebMCP tools to ordinary visitors on sites that carry a trial token; without it the tools work only with a testing flag — impact: unblocks E10-S2, the tools reach real visitors' Chrome (trial runs Chrome 149-156) — risk: none; a wrong or expired token only hides the tools — recommend: do it, because it is the only step between the shipped tools and visitors — why Jordi: it needs a Google account sign-in on the origin-trial page — steps: open https://developer.chrome.com/origintrials, pick WebMCP, Register, origin https://epicspine.dev, then paste the token via the T3 secret card or in chat (it is public, it ships in the page) — unblocks: E10-S2 — effort: ~5 min — answer: Why can't you do it yourself? Can you not use the browser? What's stopping you?

## Non-Goals

Tools that change anything or send data anywhere; WebMCP on the book pages; other browsers' polyfills.

## Issue Ledger

Steps: each is independently testable and closes only with evidence.

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| E10-S1 | Ticket worker | seat7 (T3 delegate) | Register read-only WebMCP tools in index.html, feature-detected, with a test | active | none | wt/e10-s1-webmcp | main | none | 2026-11-02 | build on branch, push, report |
| E10-S2 | Ticket worker | Delivery manager | Add the origin-trial token meta tag for epicspine.dev | blocked | E10-S1, E10-A1 | main (meta tag in index.html) | main | none | 2026-11-02 | add the token once Jordi provides it |

## Decisions

One line per decision; detail goes to a linked page.

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-11-02 | accepted | Created as a goal under epicspine-operating-system | one node in the epic log | EPIC-0-OPERATING-SYSTEM.md | never |

## Operating Learnings

None yet: one line each, `L-<n> | applies when | rule | why | confirmed <date>` (references/learnings.md).
