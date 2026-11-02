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
Status: ready
Last attempted: scaffolded with spine_new.py on 2026-11-02
Result: created, not started
Evidence: EPIC-0-OPERATING-SYSTEM.md
Waiting on: E10-A1 Jordi: register epicspine.dev for the Chrome WebMCP origin trial (developer.chrome.com/origintrials, needs a Google sign-in) and paste the token; the code ships without it and works behind the flag
Approved work: readied by Jordi 2026-11-02 ("do epicspine and zenod dev")
Next action: worker builds and tests the tools on a branch; Delivery manager verifies and integrates
Source revision: uncommitted scaffold
Verified at: 2026-11-02

## Non-Goals

Tools that change anything or send data anywhere; WebMCP on the book pages; other browsers' polyfills.

## Issue Ledger

Steps: each is independently testable and closes only with evidence.

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| E10-S1 | Ticket worker | worker | Register read-only WebMCP tools in index.html, feature-detected, with a test | ready | none | wt/e10-s1-webmcp | main | none | 2026-11-02 | build on branch, push, report |

## Decisions

One line per decision; detail goes to a linked page.

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-11-02 | accepted | Created as a goal under epicspine-operating-system | one node in the epic log | EPIC-0-OPERATING-SYSTEM.md | never |

## Operating Learnings

None yet: one line each, `L-<n> | applies when | rule | why | confirmed <date>` (references/learnings.md).
