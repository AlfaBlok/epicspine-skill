"""Standing approvals (docs/doctrine/standing-approvals.md): grant lines, `grants` in spines.py --json (own + inherited, uses), advisory checks (hermetic)."""
from __future__ import annotations

import datetime
import sys
import unittest
from pathlib import Path

import test_epic_log as T
from test_human_asks import TreeCase

sys.path.insert(0, str(T.SCRIPTS))
import grants as G  # noqa: E402
import validate_spine as v  # noqa: E402

TODAY = datetime.date(2026, 10, 24)
FULL = "- [grant E4-G1 @Jordi since 2026-10-24] Deploy and roll back the app — limits: own app only — expires: 2026-12-31 — context: https://example.com/why#g1"
WHATGPT = ("- [grant E0-G7 @Jordi since 2026-10-24] spend: LLM/STT test spend (OpenRouter, Groq) up to EUR 25 per wave; above that is an ask")
REVOKED = "- [revoked E4-G2 2026-10-25 @Jordi] Stripe test mode — why: moved to live review"
EXPIRED = "- [grant E4-G3 @Ana since 2026-09-01] Scratch DBs — expires: 2026-10-01"


def section(*lines: str, decisions: str = "") -> str:
    return "## Standing approvals\n\nThey apply to every child epic.\n\n" + "\n".join(lines) + "\n\n## Decisions\n\n" + decisions + "\n"


def parse(*lines: str, problems: list[str] | None = None) -> list[dict]:
    return G.grants(section(*lines), Path("-"), Path("-"), problems, TODAY)


class ParseTests(unittest.TestCase):
    def test_every_field(self) -> None:
        self.assertEqual([{"code": "E4-G1", "who": "Jordi", "scope": "Deploy and roll back the app", "limits": "own app only", "expires": "2026-12-31",
                           "context": "https://example.com/why#g1", "since": "2026-10-24", "state": "active", "revoked": None, "why": None}], parse(FULL))

    def test_whatgpt_line_as_written_is_scope_with_inline_limits(self) -> None:
        got = parse(WHATGPT)[0]
        self.assertEqual(("E0-G7", "active", None, None), (got["code"], got["state"], got["limits"], got["expires"]))
        self.assertTrue(got["scope"].startswith("spend: LLM/STT") and got["scope"].endswith("above that is an ask"))

    def test_states(self) -> None:
        self.assertEqual(["active", "revoked", "expired"], [g["state"] for g in parse(FULL, REVOKED, EXPIRED)])
        revoked = parse(REVOKED)[0]
        self.assertEqual(("Jordi", "2026-10-25", "moved to live review", None), (revoked["who"], revoked["revoked"], revoked["why"], revoked["since"]))
        self.assertEqual("active", parse(FULL.replace("2026-12-31", "never"))[0]["state"])
        self.assertEqual("active", parse(EXPIRED.replace("2026-10-01", "2026-10-24"))[0]["state"])  # the expiry day still holds

    def test_prose_is_skipped_and_bad_bullets_warn(self) -> None:
        problems: list[str] = []
        self.assertEqual([], parse("- grant E4-G1: deploy", "- [grant E4-1 @Jordi since 2026-10-24] x", problems=problems))
        self.assertEqual(2, len(problems))
        self.assertIn("[grant <epic code>-G<n>", problems[0])
        self.assertEqual([], G.grants("## Waiting on\n\n" + FULL + "\n", Path("-"), Path("-")))  # only under its own section


class UsesTests(unittest.TestCase):
    def test_under_codes_count_once_per_row(self) -> None:
        rows = ("| 2026-10-25 | accepted | Created db under E4-G1 | x | y | z |\n| 2026-10-26 | accepted | Deployed under E4-G1, E4-G3 and E0-G7 (E4-G1 again) | x | y | z |\n"
                "| 2026-10-24 | accepted | Standing approvals E4-G1..G3 granted | x | y | z |")
        self.assertEqual({"E4-G1": 2, "E4-G3": 1, "E0-G7": 1}, G.uses([section(decisions=rows)]))


class IssueTests(unittest.TestCase):
    def test_reused_code_and_citing_an_ended_grant(self) -> None:
        rows = "| 2026-10-26 | accepted | Replayed events under E4-G2 | x | y | z |\n| 2026-09-15 | accepted | Made a scratch db under E4-G3 | x | y | z |\n| 2026-10-02 | accepted | Again under E4-G3 | x | y | z |"
        issues = G.grant_issues(section(FULL, REVOKED, EXPIRED, FULL.replace("Deploy", "Build"), decisions=rows), today=TODAY)
        self.assertEqual(1, sum("E4-G1 is used twice" in i for i in issues))
        self.assertEqual(["2026-10-26", "2026-10-02"], [i.split()[2] for i in issues if "acts under" in i])

    def test_clean_whatgpt_bundle_has_no_issues(self) -> None:
        self.assertEqual([], G.grant_issues(section(WHATGPT, FULL), today=TODAY))


class TreeTests(TreeCase):
    def add(self, path: Path, *lines: str, decisions: str = "") -> None:
        text = path.read_text()
        text = text.replace("## Decisions\n", "## Decisions\n\n" + decisions + "\n", 1) if decisions else text
        path.write_text(text + "\n## Standing approvals\n\n" + "\n".join(lines) + "\n")

    def test_empty_by_default(self) -> None:
        self.assertEqual([], self.node()["grants"])

    def test_own_and_inherited_with_source_and_uses(self) -> None:
        root = self.repo / "docs/root.md"
        self.add(root, WHATGPT)
        self.add(self.path, FULL, decisions="| 2026-10-25 | accepted | Raised spend under E0-G7 | x | y | z |\n")
        nodes = {n["path"]: n for n in self.log()["nodes"]}
        self.assertEqual([("E0-G7", "docs/root.md", False, 1)], [(g["code"], g["source"], g["inherited"], g["uses"]) for g in nodes["docs/root.md"]["grants"]])
        child = nodes["docs/a.md"]["grants"]
        self.assertEqual([("E4-G1", "docs/a.md", False, 0), ("E0-G7", "docs/root.md", True, 1)], [(g["code"], g["source"], g["inherited"], g["uses"]) for g in child])
        self.assertEqual({"code", "who", "scope", "limits", "expires", "context", "since", "state", "revoked", "why", "source", "inherited", "uses"}, set(child[0]))

    def test_validator_advisory_sees_the_parent_chain(self) -> None:
        self.add(self.repo / "docs/root.md", WHATGPT)
        self.add(self.path, WHATGPT)  # the child repeats the parent's code
        self.assertTrue(any("E0-G7 is used twice" in a for a in v.trackable(self.path)["advisory"]))


if __name__ == "__main__":
    unittest.main()
