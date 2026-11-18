---
from: house_decision
about: claim.py misses rows in a root EPIC.md
reply-to: AlfaBlok/house_decision
status: open
---
spines.py --claim HD-S8 --repo house_decision exited 5 'row not found' because claim.py SPINE_DIRS = (docs/spines, docs) never reads the root spine EPIC.md; --spine EPIC.md worked. Fix: include the root spine (AGENTS.md Root spine:) in find_row's default files. Hit by run_85fbf1a1 on 2026-11-18.
