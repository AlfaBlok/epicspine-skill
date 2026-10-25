"""Deploy gate and PR/CI policy block the background auto-merge; gate parsing is conservative. Hermetic (temp HOME, bare origins, fake gh)."""
from __future__ import annotations

import contextlib
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from test_auto_return import ReturnBase  # noqa: E402
from test_background_sync import git  # noqa: E402

import deploy_gate  # noqa: E402
import repo_sync  # noqa: E402
from session_sync import Clock  # noqa: E402

GATED = {"AGENTS.md": "Integration policy: main-direct\nDeploy gate: deploy/, infra/**/*.tf, Dockerfile.prod\n", "README.md": "x\n"}


class GateParsing(unittest.TestCase):
    def test_paths_and_globs_parse_and_none_means_no_gate(self) -> None:
        self.assertEqual(deploy_gate.gate("- Deploy gate: `deploy/`, `infra/**/*.tf`; ./Dockerfile.prod\n"), (["deploy/", "infra/**/*.tf", "Dockerfile.prod"], None))
        for text in ("", "Deploy gate: none\n", "Deploy gate: N/A.\n", "Deploy gate:\n", "**Deploy gate:** -\n"):
            self.assertEqual(deploy_gate.gate(text), ([], None), text)
        self.assertEqual(deploy_gate.gate("AGENTS\nDeploy gate: a/\n\nspine\nDeploy gate: b/*.sql\n")[0], ["a/", "b/*.sql"])  # AGENTS + spine

    def test_anything_that_is_not_a_path_or_glob_is_unparseable(self) -> None:
        for value in ("main", "branch main", "production", "pushes to main roll prod", "release/{a,b}", "/srv/app", "../x/", "https://x.io/a",
                      "origin/main", "deploy/ and infra/", "deploy/ (prod)", "<paths>", "deploy/, prod"):
            entries, problem = deploy_gate.gate(f"Deploy gate: {value}\n")
            self.assertEqual(entries, [], value)
            self.assertIn("not only paths or globs", problem or "", value)

    def test_matching(self) -> None:
        cases = [("deploy/", "deploy/a/b.yml", True), ("deploy", "deploy/a.yml", True), ("deploy/", "deployment/a.yml", False),
                 ("infra/**/*.tf", "infra/a/b/c.tf", True), ("infra/**/*.tf", "infra/c.tf", True), ("infra/**/*.tf", "infra/c.md", False),
                 ("*.sql", "db/x.sql", True), ("migrations/*.sql", "migrations/001.sql", True), ("migrations/*.sql", "migrations/a/001.sql", False),
                 ("Dockerfile.prod", "svc/Dockerfile.prod", True), ("Deploy/", "deploy/x", True), ("docs/x.md", "docs/x.md", True),
                 ("src/**", "src/a/b", True), ("**/prod.yml", "prod.yml", True), ("**/prod.yml", "a/b/prod.yml", True), ("a/b", "a/bc", False)]
        for entry, path, want in cases:
            self.assertEqual(deploy_gate.hit(entry, path), want, (entry, path))
        self.assertEqual(deploy_gate.touched(["x/", "deploy/"], ["docs/a.md", "deploy/a.yml"]), "deploy/")
        self.assertIsNone(deploy_gate.touched(["deploy/"], ["docs/a.md"]))

    def test_policy_text_mentioning_pr_or_ci_is_flagged(self) -> None:
        for value in ("main-direct via self-merged CI-gated PR", "main-direct (open a pull request)", "main-direct, PRs for deploys", "main-direct; ci/cd"):
            self.assertIn("mentions a PR/CI gate", deploy_gate.policy_problem(f"Integration policy: {value}\n") or "", value)
        for value in ("main-direct", "main-direct (default); specific cases, priority", "main-direct."):
            self.assertIsNone(deploy_gate.policy_problem(f"Integration policy: {value}\n"), value)


class AutoMergeGate(ReturnBase):
    def blocked(self, clone: Path) -> list[str]:
        return self.entry(clone)["mess"]

    def test_a_branch_touching_a_gated_path_is_blocked_and_an_ungated_one_still_merges(self) -> None:
        bare, clone = self.repo("z", GATED)
        self.branch(clone, "feat/deploy", {"deploy/new.yml": "a: 1\n", "docs/n.md": "n\n"})
        self.branch(clone, "feat/tf", {"infra/modules/db/main.tf": "x\n"})
        self.branch(clone, "feat/df", {"svc/Dockerfile.prod": "FROM x\n"})
        self.branch(clone, "feat/docs", {"docs/ok.md": "ok\n"})
        entry = self.entry(clone)
        self.assertEqual(entry["auto"][0], "z: merged feat/docs into main (--no-ff, pushed)")
        (mess,) = entry["mess"]
        for want in ("feat/deploy (touches Deploy gate deploy/)", "feat/tf (touches Deploy gate infra/**/*.tf)", "feat/df (touches Deploy gate Dockerfile.prod)"):
            self.assertIn(want, mess)
        self.assertEqual(git(bare, "show", "main:docs/ok.md"), "ok")
        self.assertEqual(git(bare, "ls-tree", "-r", "--name-only", "main").split().count("deploy/new.yml"), 0)
        self.assertTrue({"feat/deploy", "feat/tf", "feat/df"} <= self.local(clone))  # nothing removed, nothing lost

    def test_the_gate_applies_to_changes_and_deletions_too_and_names_the_entry(self) -> None:
        bare, clone = self.repo("z", {**GATED, "deploy/run.sh": "x\n"})
        self.branch(clone, "feat/edit", {"deploy/run.sh": "y\n"})
        self.assertIn("feat/edit (touches Deploy gate deploy/)", self.blocked(clone)[0])

    def test_the_gate_is_read_from_the_root_spine_too(self) -> None:
        bare, clone = self.repo("z", {"AGENTS.md": "Integration policy: main-direct\nRoot spine: EPIC.md\n",
                                      "EPIC.md": "# E\n\n## Current State\n\nDeploy gate: ops/\n"})
        self.branch(clone, "feat/ops", {"ops/a.sh": "x\n"})
        self.assertIn("feat/ops (touches Deploy gate ops/)", self.blocked(clone)[0])

    def test_an_unparseable_gate_blocks_the_whole_repo_and_says_why(self) -> None:
        for i, value in enumerate(("main", "pushes to the production branch roll prod", "deploy/, release")):
            with self.subTest(value):
                bare, clone = self.repo(f"u{i}", {"AGENTS.md": f"Integration policy: main-direct\nDeploy gate: {value}\n"})
                self.branch(clone, "feat/docs", {"docs/ok.md": "ok\n"})
                main_tip = git(bare, "rev-parse", "main")
                entry = self.entry(clone)
                self.assertEqual(entry["auto"], [])
                self.assertEqual(git(bare, "rev-parse", "main"), main_tip)
                self.assertIn("feat/docs (auto-merge is blocked for this repo: the Deploy gate value", entry["mess"][0])
                self.assertIn("is not only paths or globs", entry["mess"][0])
                self.assertIn("feat/docs", self.local(clone))

    def test_a_policy_mentioning_pr_or_ci_blocks_auto_merge_entirely(self) -> None:
        bare, clone = self.repo("zenod", {"AGENTS.md": "Integration policy: main-direct via self-merged CI-gated PR\n", "README.md": "x\n"})
        self.branch(clone, "feat/docs", {"docs/ok.md": "ok\n"})
        main_tip = git(bare, "rev-parse", "main")
        entry = self.entry(clone)
        self.assertEqual(entry["auto"], [])
        self.assertEqual(git(bare, "rev-parse", "main"), main_tip)
        self.assertIn("feat/docs (auto-merge is blocked for this repo: its Integration policy mentions a PR/CI gate", entry["mess"][0])

    def test_none_and_a_plain_main_direct_policy_do_not_block(self) -> None:
        bare, clone = self.repo("ok", {"AGENTS.md": "Integration policy: main-direct\nDeploy gate: none\n"})
        self.branch(clone, "feat/docs", {"docs/ok.md": "ok\n"})
        self.assertEqual(self.entry(clone)["auto"][0], "ok: merged feat/docs into main (--no-ff, pushed)")


PUBLISH = "name: Publish image\non:\n  push:\n    branches: [main]\n  workflow_dispatch: {}\njobs: {}\n"
ZENOD_POLICY = "Integration policy: main-direct via self-merged CI-gated PR (`main` requires the `ci` check: push `wt/<task>`)\n"


class WholeRepoPolicy(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def make(self, files: dict[str, str], name: str = "zenod") -> Path:
        top = self.tmp / name
        for rel, text in files.items():
            (top / rel).parent.mkdir(parents=True, exist_ok=True)
            (top / rel).write_text(text)
        return top

    def test_whole_repo_pr_or_non_main_direct_policy_without_a_gate(self) -> None:
        for value in ("main-direct via self-merged CI-gated PR", "pr-approval", "manual merges by the owner", "main-direct; PRs for everything"):
            self.assertEqual(deploy_gate.whole_repo(f"Integration policy: {value}\n"), value, value)
        for text in ("", "Integration policy: main-direct\n", "Integration policy: main-direct (inherits root)\n",
                     "Integration policy: main-direct via PR for deploys\nDeploy gate: deploy/, .github/workflows/publish.yml\n"):
            self.assertIsNone(deploy_gate.whole_repo(text), text)

    def test_the_attention_line_names_the_fix_and_the_every_push_workflow(self) -> None:
        top = self.make({"AGENTS.md": ZENOD_POLICY, ".github/workflows/publish.yml": PUBLISH,
                         ".github/workflows/ci.yml": "name: ci\non: [push, pull_request]\n",
                         ".github/workflows/deploy-docs.yml": "name: deploy\non:\n  push:\n    paths-ignore: ['docs/**']\n"})
        self.assertEqual(deploy_gate.attention(top), [
            'EpicSpine attention: zenod: Integration policy "main-direct via self-merged CI-gated PR (main requires the…" gates the '
            "whole repo through PR/CI (no Deploy gate declared), so docs/spine edits and console-written answers get stranded; "
            ".github/workflows/publish.yml run(s) on every push to main — declare Deploy gate: <paths that roll prod>, keep "
            "docs/spines main-direct, add paths-ignore for docs to the deploy workflow (references/git-doctrine.md)"])
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(deploy_gate.main(["--repo", str(top)]), 1)
        self.assertIn("gates the whole repo", out.getvalue())

    def test_the_policy_and_gate_are_read_from_the_root_spine_too(self) -> None:
        top = self.make({"AGENTS.md": "Root spine: docs/EPIC-0.md. Read its Current State.\n", "docs/EPIC-0.md": "# E\n" + ZENOD_POLICY})
        (line,) = deploy_gate.attention(top)
        self.assertNotIn("every push", line)
        (top / "docs/EPIC-0.md").write_text("# E\n" + ZENOD_POLICY + "Deploy gate: Dockerfile, .github/workflows/publish.yml\n")
        self.assertEqual(deploy_gate.attention(top), [])  # an unreadable gate (bare Dockerfile) is auto_return's to report
        (top / "docs/EPIC-0.md").write_text("# E\n" + ZENOD_POLICY + "Deploy gate: Dockerfile.prod, .github/workflows/publish.yml\n")
        self.assertEqual(deploy_gate.attention(top), [])

    def test_main_direct_and_no_policy_are_silent(self) -> None:
        for agents in ("Integration policy: main-direct\n", "# no policy\n"):
            self.assertEqual(deploy_gate.attention(self.make({"AGENTS.md": agents, ".github/workflows/publish.yml": PUBLISH}, "ok")), [])
        self.assertEqual(deploy_gate.attention(self.tmp / "missing"), [])

    def test_session_start_prints_it(self) -> None:
        top = self.make({"AGENTS.md": ZENOD_POLICY})
        subprocess.run(["git", "init", "-q", "-b", "main", str(top)], check=True)
        notes = repo_sync.run(top, Clock(), self.tmp / "home", self.tmp / "skill")
        self.assertEqual([n for n in notes if "gates the whole repo" in n], deploy_gate.attention(top))


if __name__ == "__main__":
    unittest.main()
