from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

SCRIPTS = Path(__file__).parents[1] / "skill" / "epic-spine" / "scripts"
sys.dont_write_bytecode = True
sys.path.insert(0, str(SCRIPTS))
import guard_policy as gp  # noqa: E402
from guard_lex import lex  # noqa: E402

# Commands the manager may run in its main checkout (cwd = repo; wt = linked worktree).
ALLOW = """ls -la
cat README.md | head -20
grep -rn TODO src | wc -l
git status && git log --oneline -5
git -C {wt} status --short
git diff HEAD~1 -- src/a.py
git fetch --all --prune && git status -sb
git show --stat HEAD
git branch -a
git branch -d wt/task
git remote -v
git config --get user.name
git stash list
git worktree list
git worktree add ../wt-x -b wt/x main
git worktree remove {wt}
git -C {wt} rebase main
cd {wt} && git rebase main
git merge --ff-only wt/task
git pull --ff-only
git push
git push origin main
git push -u origin wt/task
git revert --no-edit HEAD
git checkout main
git switch main
git add docs/spines/b.md && git commit -m 'spine: update'
git add docs/EPIC.md
git commit -m 'spine: state'
gh pr view 3 --json title,state
gh pr list --state open
gh pr checks 5
gh -R owner/repo issue list
gh issue create -t 'ticket' -b body
gh issue comment 12 -b done
gh api repos/a/b/pulls
gh api -X GET search/issues -f q=bug
gh api graphql -f query='query {{ viewer {{ login }} }}'
gh run view 123 --log
gh auth status
curl -s http://127.0.0.1:8000/x.html
curl -sS -o /dev/null -w '%{{http_code}}' http://127.0.0.1:8000/x.html
curl -sI https://example.com
ssh host 'git -C /srv/app status; ls /srv'
ssh -p 2222 -o BatchMode=yes host uptime
ssh host 'cat /etc/os-release | head -3'
python3 -m http.server 8765 --bind 127.0.0.1
nohup python3 -m http.server 8765 --bind 127.0.0.1 > /tmp/srv.log 2>&1 &
python3 -B -m unittest discover -s tests
python3 -m pytest -q
pytest -x tests/
npm test
npm run test
cargo test
go test ./...
make test
python3 -B skill/epic-spine/scripts/validate_spine.py --strict docs/EPIC.md
python3 ~/.claude/skills/epic-spine/scripts/skill_update.py status
python3 -c 'import json,sys; print(json.load(sys.stdin)["a"])'
gh pr view 3 --json files | python3 -c 'import json,sys; [print(f["path"]) for f in json.load(sys.stdin)["files"]]'
echo hi > /dev/null
echo note >> docs/spines/b.md
echo scratch > {scratch}/x.txt
cat <<EOF > docs/spines/new.md
Spine ID: new
EOF
find . -name '*.md' -exec grep -l Spine {{}} +
sed -n '1,20p' src/a.py
awk '{{print $1}}' src/a.py
sort -u src/a.py
kill 12345
pkill -f 'http.server 8765'
open http://127.0.0.1:8765/x.html
claude -p 'implement ticket 12' --cwd ../wt-x
codex exec 'fix the bug'
lsof -i :8765
jq .name package.json
FOO=1 env BAR=2 printenv FOO
timeout 5 git fetch
sleep 2; curl -s http://127.0.0.1:8765/ | head -3
true || echo fallback
for f in docs/*.md; do wc -l "$f"; done
echo "$(git rev-parse HEAD)"
""".strip("\n").split("\n")

# Commands that are implementation (state changes) and must be denied.
DENY = """git commit -m wip -- src/a.py
git add src/a.py && git commit -m x
git add -A && git commit -m all
git commit -am 'everything'
git add .
git clone git@github.com:a/b.git
git checkout -b feat
git checkout -- src/a.py
git reset --hard HEAD~1
git rebase main
git rebase -i HEAD~3
git push --force
git push origin +main
git push origin :old
git push --delete origin wt/x
git branch -D wt/task
git branch newbranch
git cherry-pick abc123
git stash
git stash pop
git clean -fdx
git restore src/a.py
git rm src/a.py
git tag v1.0
git remote add origin x
git config user.name x
git merge wt/task
git pull
git worktree remove --force {wt}
git init newrepo
gh repo create foo --private
gh repo edit --visibility public
gh repo delete a/b --yes
gh repo clone a/b
gh pr create --fill
gh pr merge 3 --squash
gh release create v1
gh workflow run ci.yml
gh secret set TOKEN
gh api -X POST repos/a/b/issues -f title=x
gh api repos/a/b/issues -f title=x
gh api graphql -f query='mutation {{ x }}'
ssh host
ssh host 'git clone x /srv/y'
ssh host 'rm -rf /srv/app'
ssh host 'sudo systemctl restart nginx'
ssh host bash -c 'npm install'
scp file host:/tmp/
rsync -a src/ host:/srv/
sftp host
npm install
npm i left-pad
pip install requests
pip3 install -r requirements.txt
brew install jq
yarn add lodash
cargo build --release
systemctl restart nginx
launchctl load x.plist
docker run -it ubuntu
kubectl apply -f x.yaml
sudo ls
rm -rf build
rm -rf /
mkdir src/new
touch src/new.py
cp /etc/hosts src/hosts
mv src/a.py src/b.py
chmod +x src/a.py
ln -s a src/b
echo hi > src/a.py
echo hi >> README.md
printf x | tee src/a.py
cat <<EOF > src/new.py
print(1)
EOF
sed -i '' s/a/b/ src/a.py
sed -i.bak s/a/b/ src/a.py
find . -name '*.pyc' -delete
find . -exec rm {{}} \\;
awk 'BEGIN {{ system("rm x") }}'
sort -o src/a.py src/a.py
python3 -m http.server 8000
python3 -m pip install x
python3 build.py
python3 -c 'open("x","w").write("y")'
python3 -c 'import subprocess; subprocess.run(["rm","x"])'
python3 - <<EOF
import os
os.remove("x")
EOF
node scripts/gen.js
bash deploy.sh
sh -c 'rm -rf build'
eval "rm -rf build"
echo "$(rm -rf build)"
echo `touch src/x`
curl -X POST http://x/api
curl -d 'a=1' http://x/api
curl -o src/out.json http://x/a.json
curl -O http://x/a.tar.gz
wget http://x/a.tar.gz
make deploy
dd if=/dev/zero of=src/x
open src/report.html
source deploy.sh
xargs rm < files.txt
pkill python3
killall node
""".strip("\n").split("\n")


def join_heredocs(lines: list[str]) -> list[str]:
    out, i = [], 0
    while i < len(lines):
        if "<<EOF" in lines[i]:
            j = lines.index("EOF", i)
            out.append("\n".join(lines[i:j + 1]))
            i = j + 1
        else:
            out.append(lines[i])
            i += 1
    return out


def sh(cwd: Path, *args: str) -> None:
    subprocess.run(args, cwd=cwd, check=True, capture_output=True,
                   env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})


class GuardPolicyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory(prefix="epicspine-guard-")
        base = Path(os.path.realpath(cls._tmp.name))
        cls.repo, cls.wt, cls.scratch = base / "repo", base / "wt", base / "scratch"
        cls.scratch.mkdir()
        (cls.repo / "docs" / "spines").mkdir(parents=True)
        (cls.repo / "src").mkdir()
        (cls.repo / "docs" / "spines" / "b.md").write_text("# b\n\nSpine ID: b\n")
        (cls.repo / "docs" / "EPIC.md").write_text("# E\n\nSpine ID: e\n")
        (cls.repo / "README.md").write_text("# readme\n")
        (cls.repo / "src" / "a.py").write_text("x = 1\n")
        sh(base, "git", "init", "-q", "-b", "main", str(cls.repo))
        sh(cls.repo, "git", "add", "-A")
        sh(cls.repo, "git", "commit", "-qm", "init")
        sh(cls.repo, "git", "worktree", "add", "-q", str(cls.wt), "-b", "wt/task")
        # A dirty non-spine file makes `git add -A` / `.` reach beyond the spine.
        (cls.repo / "src" / "a.py").write_text("x = 2\n")
        (cls.repo / "docs" / "spines" / "b.md").write_text("# b\n\nSpine ID: b\nStatus: x\n")

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def check(self, cmd: str, **kw) -> str | None:
        cmd = cmd.format(wt=self.wt, scratch=self.scratch)
        return gp.check_command(cmd, gp.Ctx(cwd=str(self.repo), **kw))

    def test_allowed_commands(self) -> None:
        for cmd in join_heredocs(ALLOW):
            with self.subTest(cmd=cmd):
                self.assertIsNone(self.check(cmd))

    def test_denied_commands(self) -> None:
        for cmd in join_heredocs(DENY):
            with self.subTest(cmd=cmd):
                self.assertIsNotNone(self.check(cmd))

    def test_dispatcher(self) -> None:
        disp = "python3 /opt/t3/pool.py"
        allow = ["python3 -B /x/epic-spine/scripts/dispatcher.py status", "python3 /x/epic-spine/scripts/dispatcher.py bind --repo .",
                 "/x/epic-spine/scripts/dispatcher.py pick --task T", f"python3 -B {SCRIPTS}/dispatcher.py done 3 --fail",
                 "$EPICSPINE_DISPATCHER status", '"$EPICSPINE_DISPATCHER" pick --task T',
                 "${{EPICSPINE_DISPATCHER}} done 1 --signal x", f"{disp} status", f"{disp} done 2 --fail"]
        deny = ["python3 /x/epic-spine/scripts/dispatcher.py rm", "python3 /x/epic-spine/scripts/dispatcher.py",
                "python3 /tmp/x/dispatcher.py status", "/tmp/x/dispatcher.py status", "python3 -B dispatcher.py status", "$EPICSPINE_DISPATCHER rm",
                "$EPICSPINE_DISPATCHER bind", "$EPICSPINE_DISPATCHER", "$OTHER status", f"{disp} rm",
                f"{disp} status; rm -rf x", "python3 /x/other.py status"]
        with mock.patch.dict(os.environ, {"EPICSPINE_DISPATCHER": disp}):
            for cmd in allow:
                with self.subTest(cmd=cmd):
                    self.assertIsNone(self.check(cmd))
            for cmd in deny:
                with self.subTest(cmd=cmd):
                    self.assertIsNotNone(self.check(cmd))
        self.assertIsNotNone(self.check(f"{disp} status"))  # env unset: literal form not trusted

    def test_sample_size(self) -> None:
        self.assertGreaterEqual(len(ALLOW) + len(DENY), 180)

    def test_reasons_are_specific(self) -> None:
        self.assertIn("src/a.py", self.check("git add src/a.py && git commit -m x"))
        self.assertIn("--bind 127.0.0.1", self.check("python3 -m http.server 8000"))
        self.assertIn("worktree", self.check("git rebase main"))
        self.assertIn("src/a.py", self.check("echo hi > src/a.py"))

    def test_repo_config_extends_allowlist(self) -> None:
        cmd = "tools/manifest.sh skill > MANIFEST.sha256"
        self.assertIsNotNone(self.check(cmd))
        self.assertIsNone(self.check(cmd, edit_globs=["MANIFEST.sha256"], run_prefixes=["tools/manifest.sh"]))

    def test_path_policy(self) -> None:
        ctx = gp.Ctx(cwd=str(self.repo))
        home = Path.home()
        allowed = ["docs/spines/new.md", "docs/EPIC.md", str(self.scratch / "n.txt"), "/dev/null",
                   str(home / ".claude/projects/-x/memory/note.md"), str(home / ".claude_acct2/plans/p.md"),
                   str(home / ".agents/epicspine-profile.md")]
        denied = ["src/a.py", "README.md", "src/new.py", "docs/other.md", str(home / ".agents/epicspine-allow"),
                  str(home / ".claude/settings.json")]
        for p in allowed:
            with self.subTest(allowed=p):
                self.assertTrue(gp.path_ok(p, ctx))
        for p in denied:
            with self.subTest(denied=p):
                self.assertFalse(gp.path_ok(p, ctx))
        self.assertTrue(gp.path_ok("docs/new-epic.md", ctx, content="# New\n\nSpine ID: new\n"))
        self.assertFalse(gp.path_ok("docs/new-epic.md", ctx, content="# just notes\n"))

    def test_lexer(self) -> None:
        segs = lex("a 'b c' \"d $(rm x)\" | e > f 2>&1; g && h <<EOF\nbody\nEOF\n# comment\ni")
        words = [s[0] for s in segs]
        self.assertIn(["rm", "x"], words)
        self.assertIn(["a", "b c", "d $()"], words)
        self.assertIn(("e", [(">", "f"), (">&", "1")]), [(s[0][0], s[1]) for s in segs])
        self.assertIn("body", [s[2] for s in segs])
        self.assertEqual(words[-1], ["i"])

    def test_unparseable_is_denied_not_crashing(self) -> None:
        for cmd in ("echo 'unterminated", "$(", "a >", ""):
            with self.subTest(cmd=cmd):
                self.check(cmd)  # must not raise


if __name__ == "__main__":
    unittest.main()
