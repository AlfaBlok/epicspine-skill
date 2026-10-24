# EpicSpine Book Companion: detail

Page of [EPIC-0](../EPIC-0-OPERATING-SYSTEM.md); the section there keeps status, root and a link. Fields and rules moved verbatim.

Status: active
Book root: index.html
Book steward: /root delivery manager
Chapter map: index.html (part-grouped slide index)
Leaf roots: index.html (single-file deck; leaves are slides)
Canonical registry: none
Registry row identity: none
Generated registry view: none
Author scope: slides of index.html plus tests/test_book_drift.py
Root promotion authority: Book steward
Registry write authority: read-only
Archive location: git history
Validation command: `uv run --with pytest pytest -q tests/test_book_drift.py`

Binding rule: When `Status: active`, every agent bound to this spine is also a Book author. For material research, comparison, recommendation, reusable explanation, or substantial user-facing synthesis, update or add a slide in index.html without a separate request.

Navigation rule: Every slide is reachable from the part-grouped index and links back to the Book root; the root promotes only current, foundational, or decision-significant slides.

Registry rule: No canonical registry; the Book keeps no live structured collection.
Landing exceptions: No slide for quick answers, transient status, raw logs, ticket debugging, or work with no durable user-facing knowledge.
