"""Claims (agent_team E63-S3/S4): `spines.py --claim ROW --by WHO` writes the claim into the row in one pushed commit;
a second claim is refused naming the holder; an expired lease can be taken; renew and release; a closed row is refused.
Temp repos only (a bare origin and two clones, as two hosts)."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "skill" / "epic-spine" / "scripts"
ENV = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}
SPINE = """# EPIC-9: Things

Integration policy: main-direct

## Current State

Status: active

## Issue Ledger

| Issue | Role | Owner / Assignment | Title | Status | Depends On | PR/Branch | Base | Latest Evidence | Last Verified | Next Action |
|---|---|---|---|---|---|---|---|---|---|---|
| E9-S1 | Ticket worker | unassigned | One | ready | none | none | main | none | 2026-11-02 | worker |
| E9-S2 | Ticket worker | unassigned | Two | done (approved by Jordi 2026-11-02) | none | none | main | none | 2026-11-02 | none |
"""


def git(cwd: Path, *a: str) -> str:
    return subprocess.run(["git", "-C", str(cwd), *a], capture_output=True, text=True, check=True, env=ENV).stdout.strip()


class ClaimCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="claim-test-"))
        self.origin = self.tmp / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(self.origin)], check=True, env=ENV)
        self.a = self.tmp / "hostA"
        subprocess.run(["git", "clone", "-q", str(self.origin), str(self.a)], check=True, env=ENV, capture_output=True)
        (self.a / "docs" / "spines").mkdir(parents=True)
        (self.a / "docs" / "spines" / "epic-9.md").write_text(SPINE)
        git(self.a, "add", "-A")
        git(self.a, "commit", "-q", "-m", "seed")
        git(self.a, "push", "-q", "origin", "HEAD:main")
        self.b = self.tmp / "hostB"
        subprocess.run(["git", "clone", "-q", str(self.origin), str(self.b)], check=True, env=ENV, capture_output=True)

    def tearDown(self) -> None:
        subprocess.run(["rm", "-rf", str(self.tmp)])

    def claim(self, repo: Path, *a: str, at: str = "2026-11-02T22:00Z") -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(SCRIPTS / "spines.py"), "--repo", str(repo), *a], capture_output=True, text=True, env={**ENV, "EPICSPINE_CLAIM_NOW": at})

    def row(self, ref: str) -> str:
        git(self.b, "pull", "-q", "--ff-only")
        return next(l for l in (self.b / "docs/spines/epic-9.md").read_text().split("\n") if l.startswith(f"| {ref} |"))

    def test_claim_then_second_claim_refused_naming_holder(self) -> None:
        r = self.claim(self.a, "--claim", "E9-S1", "--by", "run_A")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("| run_A — claimed 2026-11-02T22:00Z, lease until 2026-11-03T00:00Z | One | active |", self.row("E9-S1"))
        self.assertEqual(git(self.origin, "log", "-1", "--format=%s", "main"), "Claim E9-S1: run_A (lease until 2026-11-03T00:00Z)")
        r2 = self.claim(self.b, "--claim", "E9-S1", "--by", "run_B", at="2026-11-02T23:00Z")
        self.assertEqual(r2.returncode, 3)
        self.assertIn("claimed by run_A until 2026-11-03T00:00Z", r2.stderr)

    def test_expired_lease_can_be_taken_renew_and_release(self) -> None:
        self.claim(self.a, "--claim", "E9-S1", "--by", "run_A", "--lease-min", "30")
        r = self.claim(self.b, "--claim", "E9-S1", "--by", "run_B", at="2026-11-02T23:00Z")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("run_B — claimed 2026-11-02T23:00Z", self.row("E9-S1"))
        r = self.claim(self.b, "--claim", "E9-S1", "--by", "run_B", "--renew", at="2026-11-02T23:30Z")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("run_B — claimed 2026-11-02T23:00Z, lease until 2026-11-03T01:30Z", self.row("E9-S1"))
        self.assertEqual(self.claim(self.a, "--claim", "E9-S1", "--by", "run_A", "--release").returncode, 3)  # not A's
        r = self.claim(self.b, "--claim", "E9-S1", "--by", "run_B", "--release", at="2026-11-02T23:40Z")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("| unassigned | One | ready |", self.row("E9-S1"))

    def test_closed_or_missing_row_refused(self) -> None:
        self.assertEqual(self.claim(self.a, "--claim", "E9-S2", "--by", "run_A").returncode, 4)
        self.assertEqual(self.claim(self.a, "--claim", "E9-S9", "--by", "run_A").returncode, 5)

    def test_a_racing_push_is_rechecked(self) -> None:
        # host B's checkout is behind (it never pulled A's claim); its claim clones origin fresh and sees A's lease
        self.claim(self.a, "--claim", "E9-S1", "--by", "run_A")
        r = self.claim(self.b, "--claim", "E9-S1", "--by", "run_B", "--no-pull")
        self.assertEqual(r.returncode, 3)
        self.assertEqual(git(self.origin, "rev-list", "--count", "main"), "2")  # seed + A's claim only


if __name__ == "__main__":
    unittest.main()
