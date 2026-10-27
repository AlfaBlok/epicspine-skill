"""Pack validator and init (references/packs.md "Validate", "Init"; pack_validate.py, pack_checks.py, pack_init.py):
a valid change passes, each rule has a failing fixture, init then validate passes, init twice changes nothing, and the
commit hook blocks a pack repo's bad commit while a repo with no pack is untouched."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _safe_env import safe_env

SCRIPTS = Path(__file__).parents[1] / "skill" / "epic-spine" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import pack  # noqa: E402
import pack_init  # noqa: E402
import pack_validate  # noqa: E402

SOCIAL = pack.load("social")
POSTS = SOCIAL["files"]["posts"]["sections"]["rows"]["fields"]
COLS = [(k, f["column"]) for k, f in POSTS.items() if "computed" not in f]
GOOD = "I built Zenod to plan my week.<br>It is free.<br>More: https://zenod.app"
BASE = {"id": "P-0001", "date": "2026-10-27", "persona": "Writer", "kind": "post", "platform": "Reddit",
        "community": "r/productivity", "slot": "2026-10-28 09:00", "title": "How I plan", "text": GOOD, "status": "draft"}


def snapshot(root: Path) -> dict:
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file() and ".git" not in p.parts}


class Repo:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.git("init", "-q")
        pack_init.init(root, "social")
        house = root / "data/message-house.md"
        house.write_text(house.read_text().replace("## Never say\n", '## Never say\n\n- "game-changer"\n- revolutionary\n'))
        brief = root / "data/brief.md"
        brief.write_text(brief.read_text() + '| R1 | mentions "pricing" | Jordi answers pricing himself |\n')

    def git(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=self.root,
                              capture_output=True, text=True, env=safe_env())

    def ledger(self, *rows: dict) -> None:
        lines = ["# Posts ledger", "", "| " + " | ".join(c for _, c in COLS) + " |", "|" + "---|" * len(COLS)]
        lines += ["| " + " | ".join({**BASE, **r}.get(k, "") for k, _ in COLS) + " |" for r in rows]
        (self.root / "data/posts-ledger.md").write_text("\n".join(lines) + "\n")

    def commit(self) -> None:
        self.git("add", "-A")
        self.git("commit", "-qm", "base", "--no-verify")

    def issues(self, by: str | None = None) -> list[str]:
        return pack_validate.run(self.root, False, by)


class Validate(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory(prefix="epicspine-pack-")
        self.addCleanup(tmp.cleanup)
        self.repo = Repo(Path(tmp.name))
        self.repo.ledger({}, {"id": "P-0002", "status": "scheduled", "slot": "2026-10-29 09:00", "community": "r/other"})
        self.repo.commit()

    def after(self, by: str | None, *rows: dict) -> str:
        self.repo.ledger(*rows, {"id": "P-0002", "status": "scheduled", "slot": "2026-10-29 09:00", "community": "r/other"})
        return "\n".join(self.repo.issues(by))

    def test_init_then_validate_passes_and_a_good_schedule_passes(self) -> None:
        self.assertEqual([], self.repo.issues())
        self.assertEqual("", self.after("Writer", {"status": "scheduled"}))
        self.assertEqual("", self.after(None, {"status": "scheduled"}))

    def test_missing_column(self) -> None:
        path = self.repo.root / "data/posts-ledger.md"
        path.write_text(path.read_text().replace("| Status |", "| State |"))
        self.assertEqual(["pack social: data/posts-ledger.md: missing column(s) Status"], self.repo.issues())

    def test_bad_enum_and_id(self) -> None:
        out = self.after(None, {"id": "P-1", "kind": "story"})
        self.assertIn("P-1: Id 'P-1' does not match", out)
        self.assertIn("Kind 'story' not one of post, reply, outreach", out)

    def test_illegal_transition(self) -> None:
        self.assertIn("P-0002: illegal status change scheduled -> draft (kind post)", self.after(None, {}, {"id": "P-0002", "status": "draft"}))
        self.assertIn("P-0001: illegal status change draft -> measured by Writer (kind post)", self.after("Writer", {"status": "measured"}))

    def test_transition_by_the_wrong_role(self) -> None:
        self.assertIn("P-0002: illegal status change scheduled -> posted by Writer", self.after("Writer", {}, {"id": "P-0002", "status": "posted", "link": "https://x.y/1"}))
        self.assertNotIn("illegal", self.after("Publisher", {}, {"id": "P-0002", "status": "posted", "link": "https://x.y/1"}))

    def test_writer_unknown_checks_legality_only(self) -> None:
        self.assertNotIn("illegal", self.after(None, {}, {"id": "P-0002", "status": "posted", "link": "https://x.y/1"}))

    def test_writer_that_is_no_role(self) -> None:
        self.assertIn("writer 'Intern' is not a role of pack social", self.after("Intern", {}))

    def test_field_writer_and_row_add(self) -> None:
        self.assertIn("P-0001: Writer may not write Feedback", self.after("Writer", {"feedback": "nice"}))
        self.assertIn("P-0003: Publisher may not add rows", self.after("Publisher", {}, {"id": "P-0003"}))

    def test_link_present_when_posted(self) -> None:
        self.assertIn("P-0002: link_present: posted without its link", self.after("Publisher", {}, {"id": "P-0002", "status": "posted"}))

    def test_disclosure(self) -> None:
        self.assertIn("P-0001: disclosure: no disclosure in the first 2 lines", self.after("Writer", {"status": "scheduled", "text": "Plan your week.<br>Free.<br>I built it"}))

    def test_link_rule(self) -> None:
        out = self.after("Writer", {"status": "scheduled", "text": "I built https://a.b<br>and https://c.d"})
        self.assertIn("link_rule: 2 links in the text (max 1)", out)
        self.assertIn("link_rule: a link on line 1", out)

    def test_never_say(self) -> None:
        out = self.after("Writer", {"status": "scheduled", "text": GOOD + "<br>A revolutionary game-changer"})
        self.assertIn("never_say: says never-say phrase 'game-changer'", out)
        self.assertIn("never_say: says never-say phrase 'revolutionary'", out)

    def test_caps(self) -> None:
        out = self.after("Writer", {"status": "scheduled", "slot": "2026-10-29 10:00"})
        self.assertIn("caps: 2 posts on Reddit on 2026-10-29 (cap 1 a day)", out)
        self.assertIn("caps: 2 posts in r/other that week", self.after("Writer", {"status": "scheduled", "community": "r/other"}))

    def test_hold_rules(self) -> None:
        text = GOOD + "<br>Our pricing is fair"
        self.assertIn("hold_rules: matches hold rule R1", self.after("Writer", {"status": "scheduled", "text": text}))
        self.assertEqual("", self.after("Writer", {"status": "held", "text": text}))

    def test_a_removed_row(self) -> None:
        self.repo.ledger({})
        self.assertIn("P-0002: row removed", "\n".join(self.repo.issues()))

    def test_reply_rows_start_at_draft_and_go_live_with_checks(self) -> None:
        reply = {"id": "P-0003", "kind": "reply", "status": "posted", "link": "https://x.y/r", "text": "Thanks!"}
        self.assertIn("P-0003: disclosure", self.after("Responder", {}, reply))
        self.assertEqual("", self.after("Responder", {}, {**reply, "platform": "X"}))


class InitAndHook(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory(prefix="epicspine-pack-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def test_init_twice_is_a_no_op_and_never_overwrites(self) -> None:
        (self.root / "data").mkdir()
        (self.root / "data/message-house.md").write_text("# Message house\n\n## Voice\n\n- plain\n")
        (self.root / "AGENTS.md").write_text("# AGENTS\n\nIntegration policy: main-direct\n")
        self.assertTrue(pack_init.init(self.root, "social"))
        house = (self.root / "data/message-house.md").read_text()
        self.assertTrue(house.startswith("# Message house\n\n## Voice\n\n- plain\n"))
        self.assertEqual(1, house.count("## Voice"))
        self.assertIn("## Never say", house)
        self.assertEqual(["social"], pack.enabled(self.root))
        before = snapshot(self.root)
        self.assertEqual([], pack_init.init(self.root, "social"))
        self.assertEqual(before, snapshot(self.root))
        self.assertEqual([], pack_validate.run(self.root, False))

    def test_init_appends_to_an_existing_root_spine_and_skips_a_missing_one(self) -> None:
        notes: list[str] = []
        pack_init.init(self.root, "social", notes)
        self.assertFalse((self.root / "docs/spines/root.md").exists())
        self.assertIn("skipped docs/spines/root.md", notes[0])
        (self.root / "docs/spines").mkdir(parents=True)
        (self.root / "docs/spines/root.md").write_text("# EPIC-0\n\n## Goal\n\nSell.\n")
        self.assertEqual(["added to docs/spines/root.md: ## Targets"], pack_init.init(self.root, "social"))

    def hook(self) -> subprocess.CompletedProcess:
        git = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run([*git, "add", "-A"], cwd=self.root, env=safe_env())
        return subprocess.run([sys.executable, "-B", str(SCRIPTS / "pre_commit.py")], cwd=self.root, capture_output=True, text=True, env=safe_env())

    def test_commit_hook_blocks_a_pack_repo_and_leaves_others_alone(self) -> None:
        subprocess.run(["git", "init", "-q"], cwd=self.root, env=safe_env())
        (self.root / "data").mkdir()
        (self.root / "data/posts-ledger.md").write_text("# Posts\n\n| Id | Status |\n|---|---|\n| P-0001 | draft |\n")
        plain = self.hook()
        self.assertEqual(0, plain.returncode, plain.stderr)
        self.assertNotIn("pack", plain.stderr)
        pack_init.init(self.root, "social")
        bad = self.hook()
        self.assertEqual(1, bad.returncode)
        self.assertIn("epicspine: pack social: data/posts-ledger.md: missing column(s) Date", bad.stderr)
        (self.root / "data/posts-ledger.md").unlink()
        pack_init.init(self.root, "social")
        good = self.hook()
        self.assertEqual(0, good.returncode, good.stderr)

    def test_cli(self) -> None:
        run = lambda *a: subprocess.run([sys.executable, "-B", str(SCRIPTS / "pack.py"), *a], capture_output=True, text=True, env=safe_env())  # noqa: E731
        self.assertIn("AGENTS.md: added Pack: social", run("init", "social", "--repo", str(self.root)).stdout)
        self.assertIn("nothing to do", run("init", "social", "--repo", str(self.root)).stdout)
        done = run("validate", "--repo", str(self.root))
        self.assertEqual((0, "ok (social)\n"), (done.returncode, done.stdout))


if __name__ == "__main__":
    unittest.main()
