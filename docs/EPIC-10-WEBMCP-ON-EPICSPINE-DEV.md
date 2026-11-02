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
Waiting on: Jordi: E10-A2 (S1 does not wait on it)
Approved work: readied by Jordi 2026-11-02 ("do epicspine and zenod dev")
Next action: worker builds and tests the tools on a branch; Delivery manager verifies and integrates
Source revision: uncommitted scaffold
Verified at: 2026-11-02

## Waiting on

- [answered E10-A1 2026-11-02 @Jordi · done 2026-11-02] Register epicspine.dev for Chrome's WebMCP origin trial and give us the token — context: Chrome only shows WebMCP tools to ordinary visitors on sites that carry a trial token; without it the tools work only with a testing flag — impact: unblocks E10-S2, the tools reach real visitors' Chrome (trial runs Chrome 149-156) — risk: none; a wrong or expired token only hides the tools — recommend: do it, because it is the only step between the shipped tools and visitors — why Jordi: it needs a Google account sign-in on the origin-trial page — steps: open https://developer.chrome.com/origintrials, pick WebMCP, Register, origin https://epicspine.dev, then paste the token via the T3 secret card or in chat (it is public, it ships in the page) — unblocks: E10-S2 — effort: ~5 min — answer: Why can't you do it yourself? Can you not use the browser? What's stopping you? — research (Unblocker 2026-11-02): an agent can do almost all of it; the only thing stopping it is a Google sign-in. Checked: the agents' own browser (T3 shared browser on vps3, Default profile) opens developer.chrome.com/origintrials but shows "Please sign in to view your registrations" (no Google account); the Team Browser on vps1 holds only Airbnb, Reddit and X sessions (no Google) and has no general click/type tool; Google sessions are device-bound, so copying cookies from the Mac is not reliable (agent_team M4 limits); the trial token is signed by Google per registered origin, so there is no route without an account. — recommend: Jordi signs in to Google once in the agents' shared browser (E10-A2); an agent then registers https://epicspine.dev for WebMCP, copies the token and ships the meta tag (E10-S2) itself.
- [ask E10-A2: do @Jordi since 2026-11-02 row E10-S2] Sign in to your Google account once in the agents' shared browser, so an agent can register the WebMCP trial itself — context: you asked why agents can't do E10-A1 themselves; they can, except the sign-in: their browser has no Google login and Google blocks copied logins — impact: unblocks E10-S2, the WebMCP tools reach visitors' Chrome without a flag; after the sign-in the agent does the rest (register, token, page) — risk: the shared browser keeps your Google session on the agent box; rollback: sign out in that tab, or remove the device at myaccount.google.com/device-activity — recommend: do it, about one minute; use a Google account you are fine with agents using for developer sites — why Jordi: only you can enter your Google password and 2-step code — steps: open the T3 browser preview on https://developer.chrome.com/origintrials, click Sign in, finish Google's sign-in, then answer "signed in" here — unblocks: E10-S2 — effort: ~1 min

## Non-Goals

Tools that change anything or send data anywhere; WebMCP on the book pages; other browsers' polyfills.

## Issue Ledger

Steps: each is independently testable and closes only with evidence.

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| E10-S1 | Ticket worker | seat7 (T3 delegate) | E10-1..2: Register read-only WebMCP tools in index.html, feature-detected, with a test | active | none | wt/e10-s1-webmcp | main | none | 2026-11-02 | build on branch, push, report |
| E10-S2 | Ticket worker | Delivery manager | E10-3: Add the origin-trial token meta tag for epicspine.dev | blocked | E10-S1, E10-A2 | main (meta tag in index.html) | main | none | 2026-11-02 | after E10-A2, register https://epicspine.dev in the T3 shared browser, add the token meta tag |

## Decisions

One line per decision; detail goes to a linked page.

| Date | Outcome | Decision / Attempt | Durable Summary | Evidence | Revisit When |
|---|---|---|---|---|---|
| 2026-11-02 | accepted | Created as a goal under epicspine-operating-system | one node in the epic log | EPIC-0-OPERATING-SYSTEM.md | never |
| 2026-11-02 | accepted | decided by Unblocker: E10-A1 split on Jordi's "Why can't you do it yourself?": an agent registers the WebMCP trial and ships the token; only the Google sign-in stays with Jordi (E10-A2) — why: the agent browser and Team Browser hold no Google session and Google logins cannot be copied in; everything after the sign-in is agent work — rollback: delete E10-A2 and restore E10-A1's steps | only the Google sign-in is Jordi's (E10-A2); trial registration and token are agent work | E10-A1 research note; origintrials "Please sign in" seen 2026-11-02 | when Jordi answers E10-A2 |

## Operating Learnings

None yet: one line each, `L-<n> | applies when | rule | why | confirmed <date>` (references/learnings.md).
