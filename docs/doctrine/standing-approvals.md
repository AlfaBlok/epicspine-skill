# Standing approvals: contract (v1)

Page of [EPIC-0](../EPIC-0-OPERATING-SYSTEM.md) ticket-35 (agent_team EPIC-8 E8-S1, Jordi, 2026-10-24). Companion of [human-asks.md](human-asks.md): an ask is one human action that blocks the next step; a standing approval is a yes given up front, so the action needs no ask. First live use: whatgpt_v3 `docs/EPIC-0-ROOT.md` E0-G1..G10.

Most asks are careful agents asking "may I?" for things the build obviously needs. So at kickoff the delivery manager foresees what the build will need and asks once; personas then act inside the grants without asking.

## Writing a grant
One line per grant under `## Standing approvals`, right after `## Waiting on` (prose around the lines is allowed and ignored):

```
## Standing approvals
- [grant E4-G1 @Jordi since 2026-10-24] Create, configure, deploy and roll back the Dokploy app `whatgpt-service` — limits: no change to other apps or Dokploy settings — expires: never — context: [plan](docs/plan.md#infra)
```

**Tag:** `[grant <code> @<who> since <YYYY-MM-DD>]`
- `code` is `<epic code>-G<n>`, like an ask code (`E4-G1`, `EPIC-4-G2`). `n` counts up per epic and is never reused: take the highest G-number in the section, plus 1. Across repos qualify it `<repo>/<code>`.
- `who` is the human who granted it; `since` the date it was granted.

**Then:** the scope, one sentence: what the agents may do, concretely enough that a reader can tell whether an action is inside it. Limits may sit inline in the scope (`…; no change to other databases`), as the whatgpt lines do.

**Then the optional fields, each introduced by ` — `:** `limits:` (what stays outside), `expires:` (`<YYYY-MM-DD>` or `never`; absent means never), `context:` (a page or anchor with the background).

## States
- **active**: a `grant` line whose `expires:` is absent, `never`, or today or later.
- **expired**: `expires:` is a date before today. Nothing to rewrite; the line stays as history until cleaned up.
- **revoked**: the owner rewrites the line as `- [revoked <code> <YYYY-MM-DD> @<who>] <scope> — why: <reason>` (`who` is the human who revoked it) and adds a Decisions row citing the code.

A revoked or expired line may be deleted once a Decisions row cites the code. Codes are never reused.

## Inheritance
A grant applies to its spine and to every descendant through `Parent spine:`. A child may narrow it (a grant of its own with a smaller scope, its own code), never widen it: a child cannot grant what its parent's grants leave outside, only the human can, by a new grant on the spine that owns the scope. Revoking a parent grant revokes it for the whole subtree.

## Using a grant
- An action inside an active grant (own or inherited) is not an ask: do it, then record a Decisions row that cites the code as `under <code>` (`under E0-G1, E0-G3` for several). That is how uses are counted.
- An action outside every active grant follows the ask tier ([human-asks.md](human-asks.md)). Spending past a grant's limit is outside it.
- Doubt about whether an action is inside the scope means it is outside: ask, and the answer may become a new grant.

## Kickoff pattern
At a goal's kickoff (or a wave's), the delivery manager lists what the build will need from the human (accounts, infra it owns, spend ceilings, test-only side effects) and proposes it as ONE `approve` ask whose question carries the bundle. On approval it writes the grant lines (the answer write-back of human-asks.md: the ask becomes `answered`, a Decisions row cites the ask code, the lines appear under `## Standing approvals`). Publishing, live money and shared infra are never in a default bundle; propose them only by name.

## In `spines.py --json` (per node)
```json
"grants": [{"code": "E0-G7", "who": "Jordi", "scope": "spend: LLM/STT test spend (OpenRouter, Groq) up to EUR 25 per wave; above that is an ask",
            "limits": null, "expires": null, "context": null, "since": "2026-10-24", "state": "active", "revoked": null, "why": null,
            "source": "docs/EPIC-0-ROOT.md", "inherited": true, "uses": 2}]
```
- `grants` holds this node's own grants first, then every ancestor's (nearest first), `[]` when none. `source` is the repo-relative spine that defines the line; `inherited` is true when that is an ancestor.
- `state` is `active`, `expired` or `revoked`; `revoked` is the revoke date and `why` its reason (else null; `since` is null on a revoked line). `context` is repo-relative when local, an external URL as-is. Missing fields are null.
- `uses` counts the Decisions rows, over every spine of the tree, that cite the code as `under <code>` (a row counts once per code).

## Checks (advisory; they never block a commit)
The validator (`--trackable` `advisory`) and the commit hook warn on: a `## Standing approvals` bullet the tools cannot read (naming the canonical form); a code used twice in the spine or repeated from an ancestor; a Decisions row dated after a grant expired or was revoked that still acts `under` it. A child widening a parent grant is not detectable from text and is not checked; reviewers check it.
