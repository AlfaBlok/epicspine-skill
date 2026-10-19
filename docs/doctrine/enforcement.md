# Doctrine enforcement plan

Page of [EPIC-4](../EPIC-4-DOCTRINE-2.md), step 2. Approved together with the doctrine page.

The doctrine is one current definition, with no version line. It is enforced in four places. Required means blocked on new epics only; everything else is advisory.

## 1. Scaffold: new epics start compliant
`spine_new.py` writes an `EPIC-<n>: <name>` title, taking the next code from E3-2. Below the title it writes:
- `## Goal`, `## Serves` (with a link to the parent);
- `## Done means` (2-5 checkbox outcomes, above the steps);
- `## Current State` with one `Status:` word;
- the steps ledger, Decisions (one line each) and Learnings.

It also adds a "contributes" sentence for the new epic in the parent's Spine Map. It writes no `Spine Type:` line and no version line.

## 2. Commit check: new epics are blocked; old ones keep passing
`pre_commit.py` blocks only an epic file *added* in the commit that lacks one of these:
- the title;
- Goal (Mission counts);
- Serves (not needed for the root);
- Done means;
- the Status word.

Existing epics are never blocked. These are advisory warnings only:
- missing sections on existing epics;
- size budget: an epic over 150 lines, or a table cell over 200 characters (proposed numbers);
- a page that "looks like an epic" (it has Goal, Done means, checkbox outcomes, Next action or Status), because intent belongs in an epic;
- orphan pages.

`--strict` stays advisory.

## 3. Visibility: readers see the story
`spines.py --json` adds the doctrine fields to each epic (contract: [console-contract.md](console-contract.md)):
- `goal`, `serves`, `done_means`;
- each child's `contributes`;
- `pages` (by inbound links, any depth);
- `missing_sections`;
- `size`.

Discovery follows epic parent links and page inbound links. A doc no tree leaf links to is an orphan. Status rolls up to the nearest epic ancestor. The agent_team console renders these fields; it is built in parallel against the contract (step 4).

## 4. Migration: "make it compliant"
An agent asked to make an epic compliant:
1. reads `missing_sections` from `spines --json`;
2. fills each gap from facts already in the repo, and asks the epic's owner for any "why" that is not written down, never inventing one;
3. slims the epic to its own level, moving detail into linked pages;
4. links those pages;
5. commits.

SKILL.md carries this in one line. A step is closed only with evidence: the ledger's Latest Evidence column is the step's test. Recording includes passing a major finding up to the parent.

**For Jordi to confirm:** the advisory size numbers (150 lines per epic, 200 characters per cell).
