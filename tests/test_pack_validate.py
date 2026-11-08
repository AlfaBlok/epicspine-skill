"""Pack validator and init (references/packs.md "Validate", "Init"; pack_validate.py, pack_checks.py, pack_init.py):
a valid change passes, each rule has a failing fixture, init then validate passes, init twice changes nothing, and the
commit hook blocks a pack repo's bad commit while a repo with no pack is untouched."""
from __future__ import annotations

import contextlib
import io
import json
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
        brief = root / "data/brief.md"
        text = brief.read_text().replace("## Never say\n", '## Never say\n\n- "game-changer"\n- revolutionary\n')
        hold = "## Hold for me\n\n| Id | Hold a post when | Why |\n|---|---|---|\n"
        assert hold in text, "init writes the hold rules table into data/brief.md"
        brief.write_text(text.replace(hold, hold + '| R1 | mentions "pricing" | Jordi answers pricing himself |\n'))

    def git(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=self.root,
                              capture_output=True, text=True, env=safe_env())

    def ledger(self, *rows: dict) -> None:
        lines = ["# Posts ledger", "", "| " + " | ".join(c for _, c in COLS) + " |", "|" + "---|" * len(COLS)]
        lines += ["| " + " | ".join({**BASE, **r}.get(k, "") for k, _ in COLS) + " |" for r in rows]
        (self.root / "data/posts-ledger.md").write_text("\n".join(lines) + "\n")

    def messages(self, chats: list[dict], msgs: list[dict]) -> None:
        sec = SOCIAL["files"]["messages"]["sections"]
        out = ["# Messages ledger", ""]
        for key, rows in (("chats", chats), ("messages", msgs)):
            cols = [(k, f["column"]) for k, f in sec[key]["fields"].items() if "computed" not in f]
            out += [f"## {sec[key]['heading']}", "", "| " + " | ".join(c for _, c in cols) + " |", "|" + "---|" * len(cols)]
            out += ["| " + " | ".join(r.get(k, "") for k, _ in cols) + " |" for r in rows] + [""]
        (self.root / "data/messages-ledger.md").write_text("\n".join(out))

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

    def test_a_new_post_names_a_benefit_that_works_today_when_the_brief_has_a_benefits_home(self) -> None:
        brief = self.repo.root / "data/brief.md"
        self.assertEqual("", self.after("Writer", {"status": "scheduled"}))  # no Benefits section: the repo is not asked, and not failed for it
        brief.write_text(brief.read_text() + "\n## Benefits\n\n| # | Benefit | Status | Screen |\n|---|---|---|---|\n"
                         "| 1 | You drop in loose ideas, and a writer turns them into posts. | works today | https://example.com/pipeline.png |\n"
                         "| 2 | A researcher reads your competitors. | half built | |\n")
        self.repo.ledger({}, {"id": "P-0002", "status": "scheduled", "slot": "2026-10-29 09:00", "community": "r/other"})
        self.repo.commit()  # Jordi's table is part of HEAD: the Writer is not judged for adding it
        none = self.after("Writer", {"status": "scheduled"})
        self.assertIn("benefit_named: names no benefit", none)
        self.assertEqual("", self.after("Writer", {"status": "scheduled", "benefit": "1"}))
        self.assertIn("benefit_named: benefit 2 is half built", self.after("Writer", {"status": "scheduled", "benefit": "2"}))
        self.assertIn("names no benefit", self.after("Writer", {"status": "held", "benefit": "9"}))
        reply = self.after("Responder", {"status": "posted", "kind": "reply", "link": "https://x.com/a/1"})
        self.assertNotIn("benefit_named", reply)  # only a new post names a benefit, never a reply

    def test_a_benefit_status_is_one_of_three_words(self) -> None:
        brief = self.repo.root / "data/brief.md"
        brief.write_text(brief.read_text() + "\n## Benefits\n\n| # | Benefit | Status | Screen |\n|---|---|---|---|\n| 1 | A line. | soonish | |\n")
        self.assertIn("Status 'soonish' not one of works today, half built, not built", "\n".join(self.repo.issues()))

    def test_missing_column(self) -> None:
        path = self.repo.root / "data/posts-ledger.md"
        path.write_text(path.read_text().replace("| Status |", "| State |"))
        self.assertEqual(["pack social: data/posts-ledger.md: missing column(s) Status"], self.repo.issues())

    def test_campaign_column_is_optional_and_writable_by_row_writers_and_jordi(self) -> None:
        # agent_team E60-S1: a ledger without Campaign stays valid; with it, the row's writers and Jordi tag a row.
        self.assertNotIn("missing column", "\n".join(self.repo.issues()))
        self.assertIn("Campaign", " ".join(c for _, c in COLS))
        self.assertEqual("", self.after("Writer", {"campaign": "EPIC-7"}))
        self.repo.commit()
        self.assertEqual("", self.after("Jordi", {"campaign": "EPIC-8"}))
        self.assertIn("Publisher may not write Campaign", self.after("Publisher", {"campaign": ""}))

    def test_a_ledger_without_the_campaign_column_is_valid(self) -> None:
        cols = [(k, c) for k, c in COLS if c != "Campaign"]
        lines = ["# Posts ledger", "", "| " + " | ".join(c for _, c in cols) + " |", "|" + "---|" * len(cols)]
        lines += ["| " + " | ".join(BASE.get(k, "") for k, _ in cols) + " |"]
        (self.repo.root / "data/posts-ledger.md").write_text("\n".join(lines) + "\n")
        self.assertNotIn("missing column", "\n".join(self.repo.issues()))

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

    def test_writer_adds_the_diagram_of_its_post_scout_may_not(self) -> None:
        assets = self.repo.root / "data/assets.md"
        assets.write_text(assets.read_text() + "| A-1 | diagram | data/assets/A-1-goal-tree.png | Writer | data/assets/A-1-goal-tree.json |  |\n")
        self.assertEqual([], self.repo.issues("Writer"))
        self.assertIn("A-1: Scout may not add rows", "\n".join(self.repo.issues("Scout")))

    def test_video_maker_registers_its_clip_publisher_may_not(self) -> None:
        assets = self.repo.root / "data/assets.md"
        assets.write_text(assets.read_text() + "| A-2 | clip | data/assets/demo-01/master.mp4 | Video Maker | library clip demo-01 | x: x.mp4 |\n")
        self.assertEqual([], self.repo.issues("Video Maker"))
        self.assertIn("A-2: Publisher may not add rows", "\n".join(self.repo.issues("Publisher")))

    def test_jordi_drops_an_idea_new_or_picked_up_to_parked_only(self) -> None:
        ideas = self.repo.root / "data/ideas.md"
        head = ideas.read_text()

        def rows(*states: str) -> str:
            ideas.write_text(head + "".join(f"| I-{n} | 2026-10-27 | idea {n} | text | Reddit | Jordi | | {s} | |\n"
                                            for n, s in enumerate(states, 1)))
            return "\n".join(self.repo.issues("Jordi"))

        rows("new", "picked up", "epic")
        self.repo.commit()
        self.assertEqual("", rows("parked", "parked", "epic"))
        self.assertIn("I-3: illegal state change epic -> parked by Jordi", rows("new", "picked up", "parked"))
        self.assertIn("I-1: illegal state change new -> picked up by Jordi", rows("picked up", "picked up", "epic"))

    def test_link_present_when_posted(self) -> None:
        self.assertIn("P-0002: link_present: posted without its link", self.after("Publisher", {}, {"id": "P-0002", "status": "posted"}))

    def test_disclosure(self) -> None:
        self.assertIn("P-0001: disclosure: no disclosure in the first 2 lines", self.after("Writer", {"status": "scheduled", "text": "Plan your week.<br>Free.<br>I built it"}))

    def test_link_rule(self) -> None:
        out = self.after("Writer", {"status": "scheduled", "text": "I built https://a.b<br>and https://c.d"})
        self.assertIn("link_rule: 2 links in the text (max 1)", out)
        self.assertIn("link_rule: a link on line 1", out)

    def test_link_rule_reads_the_paragraph_mark_as_a_line(self) -> None:
        # agent_team E61-S7 (P-0062): the ledger joins paragraphs with " · "; a link in paragraph 2 is not on line 1
        text = "I built Zenod, so this is my own project. · Here is the clip: https://a.b/c.mp4 It shows the fix. · What do you use?"
        self.assertNotIn("link_rule", self.after("Writer", {"status": "scheduled", "text": text}))
        self.assertIn("link_rule: a link on line 1", self.after("Writer", {"status": "scheduled", "text": "I built it: https://a.b · What do you use?"}))
        self.assertIn("disclosure: no disclosure in the first 2 lines",
                      self.after("Writer", {"status": "scheduled", "text": "Plan your week. · Free. · I built it"}))

    def test_never_say(self) -> None:
        out = self.after("Writer", {"status": "scheduled", "text": GOOD + "<br>A revolutionary game-changer"})
        self.assertIn("never_say: says never-say phrase 'game-changer'", out)
        self.assertIn("never_say: says never-say phrase 'revolutionary'", out)

    def test_caps(self) -> None:
        out = self.after("Writer", {"status": "scheduled", "slot": "2026-10-29 10:00"})
        self.assertIn("caps: 2 posts on Reddit on 2026-10-29 (cap 1 a day)", out)
        self.assertIn("caps: 2 posts in r/other that week", self.after("Writer", {"status": "scheduled", "community": "r/other"}))

    def test_caps_x_takes_three_posts_a_day(self) -> None:
        # agent_team E78-S1 (the 15-day push): X has its own cap of 3 posts a day; Reddit keeps 1.
        x = {"platform": "X", "status": "scheduled", "slot": "2026-10-30 09:00", "community": ""}
        two = self.after("Writer", {**x, "id": "P-0010"}, {**x, "id": "P-0011", "slot": "2026-10-30 12:00"})
        self.assertNotIn("caps:", two)
        four = self.after("Writer", *[{**x, "id": f"P-001{i}", "slot": f"2026-10-30 1{i}:00"} for i in range(4)])
        self.assertIn("caps: 4 posts on X on 2026-10-30 (cap 3 a day)", four)

    def test_caps_community_week_only_on_community_platforms(self) -> None:
        # agent_team E78-S5: X rows carry the account (@ZenodAgent) as their community; the weekly cap per
        # community is Reddit's (subreddits), so X takes 3 a day all week; a Reddit community stays at 1 a week.
        x = {"platform": "X", "status": "scheduled", "community": "@ZenodAgent"}
        rows = [{**x, "id": f"P-002{i}", "slot": f"2026-10-{27 + i // 3} 1{i % 3}:00"} for i in range(6)]
        self.assertNotIn("caps:", self.after("Writer", *rows))
        self.assertNotIn("caps:", self.after("Writer", *rows[:3]))
        self.assertIn("caps: 2 posts in r/other that week (cap 1 a week)",
                      self.after("Writer", {"status": "scheduled", "slot": "2026-10-27 09:00", "community": "r/other"}))

    def test_hold_rules(self) -> None:
        text = GOOD + "<br>Our pricing is fair"
        self.assertIn("hold_rules: matches hold rule R1", self.after("Writer", {"status": "scheduled", "text": text}))
        self.assertEqual("", self.after("Writer", {"status": "held", "text": text}))

    def test_approval_gate_held_to_scheduled_needs_jordis_approved_note(self) -> None:
        # agent_team E46-S2: a campaign that wants every post approved holds them all (hold rule `Kind: post`);
        # Jordi's Approve writes "Approved" in Feedback; with feedback, the Writer applies it and schedules it.
        held = {"status": "held", "slot": "2026-10-30 09:00"}
        self.assertEqual("", self.after("Writer", held))
        self.repo.commit()
        self.assertIn("P-0001: approved: no approval from Jordi in feedback", self.after("Jordi", {**held, "status": "scheduled"}))
        self.assertIn("P-0001: approved: no approval from Jordi", self.after("Writer", {**held, "status": "scheduled"}))
        self.assertEqual("", self.after("Jordi", {**held, "status": "scheduled", "feedback": "Approved 2026-11-01"}))
        self.after("Jordi", {**held, "feedback": "Approved with feedback 2026-11-01: say it shorter"})
        self.repo.commit()
        approved = {**held, "feedback": "Approved with feedback 2026-11-01: say it shorter"}
        self.assertEqual("", self.after("Writer", {**approved, "status": "scheduled", "text": GOOD + "<br>Shorter."}))
        self.assertIn("never_say: says never-say phrase", self.after("Writer", {**approved, "status": "scheduled", "text": GOOD + "<br>revolutionary"}))
        self.assertIn("illegal status change held -> scheduled by Publisher", self.after("Publisher", {**approved, "status": "scheduled"}))

    def test_revise_keeps_it_held_and_restore_brings_a_pulled_post_back_to_held(self) -> None:
        # agent_team E34-S22: Change it (revise) is a note, never an approval; Don't post's Undo is pulled -> held by Jordi.
        held = {"status": "held", "slot": "2026-10-30 09:00"}
        self.assertEqual("", self.after("Writer", held))
        self.repo.commit()
        revise = {**held, "feedback": "Revise requested 2026-11-02 10:00 UTC: say it shorter"}
        self.assertEqual("", self.after("Jordi", revise))
        self.repo.commit()
        self.assertEqual("", self.after("Writer", {**revise, "text": GOOD + "<br>Shorter.", "checks": "Revised 2026-11-02 10:20 UTC; pass"}))
        self.assertIn("P-0001: approved: no approval from Jordi", self.after("Writer", {**revise, "status": "scheduled"}))
        self.assertEqual("", self.after("Jordi", {**revise, "status": "pulled"}))
        self.repo.commit()
        self.assertIn("illegal status change pulled -> held by Writer", self.after("Writer", {**revise, "status": "held"}))
        self.assertEqual("", self.after("Jordi", {**revise, "status": "held"}))

    def test_restore_brings_a_pulled_post_back_to_the_status_it_had(self) -> None:
        # agent_team E34-S25: Undo after a pull of a scheduled post puts it back on schedule with its slot (pulled ->
        # scheduled by Jordi); a pulled draft is a draft again; only Jordi restores; Jordi may give a held post a new slot.
        sched = {"status": "scheduled", "slot": "2026-10-30 09:00"}
        self.assertEqual("", self.after("Writer", sched))
        self.repo.commit()
        self.assertEqual("", self.after("Jordi", {**sched, "status": "pulled"}))
        self.repo.commit()
        self.assertIn("illegal status change pulled -> scheduled by Writer", self.after("Writer", sched))
        self.assertIn("illegal status change pulled -> scheduled by Publisher", self.after("Publisher", sched))
        self.assertEqual("", self.after("Jordi", sched))
        self.assertEqual("", self.after("Jordi", {**sched, "status": "draft"}))
        self.assertEqual("", self.after("Jordi", {**sched, "status": "held"}))
        self.repo.commit()
        self.assertEqual("", self.after("Jordi", {"status": "scheduled", "slot": "2026-10-31 09:00", "feedback": "Approved 2026-10-31 08:00 UTC"}))

    def test_an_undo_is_never_a_step_of_a_longer_path(self) -> None:
        # E34-S25: pulled -> scheduled / draft / held are `alone`: no draft -> pulled -> scheduled past the Writer's checks,
        # no held -> pulled -> scheduled past the approved check, no scheduled -> pulled -> draft for an unnamed writer.
        self.assertIn("P-0001: illegal status change draft -> scheduled by Jordi", self.after("Jordi", {"status": "scheduled"}))
        self.assertIn("P-0002: illegal status change scheduled -> draft by Jordi", self.after("Jordi", {}, {"id": "P-0002", "status": "draft"}))
        self.assertEqual("", self.after("Writer", {"status": "held"}))
        self.repo.commit()
        self.assertIn("P-0001: approved: no approval from Jordi", self.after("Jordi", {"status": "scheduled"}))

    def test_a_late_post_goes_back_to_held_never_out(self) -> None:
        # agent_team E60-S2: a scheduled post whose slot passed while its campaign was retired comes back held: Jordi's
        # Restore (scheduled -> held) or the Publisher's no_late_post (scheduled -> held); nobody else holds it.
        sched = {"status": "scheduled", "slot": "2026-11-03T14:00:00Z"}
        self.assertEqual("", self.after("Writer", sched))
        self.repo.commit()
        self.assertIn("illegal status change scheduled -> held by Writer", self.after("Writer", {**sched, "status": "held"}))
        self.assertEqual("", self.after("Publisher", {**sched, "status": "held"}))
        self.assertEqual("", self.after("Jordi", {**sched, "status": "held"}))
        self.repo.commit()
        # then his Post now (Approved after the slot) puts it back for the Publisher
        self.assertEqual("", self.after("Jordi", {**sched, "feedback": "Approved 2026-11-03 15:10 UTC"}))
        rules = json.loads((SCRIPTS.parent / "packs/social/schema.json").read_text())["rules"]
        self.assertEqual("Publisher", rules["no_late_post"]["by"])
        self.assertIn("never goes out", rules["no_late_post"]["doc"])

    def test_hold_rule_kind_post_holds_every_post_and_held_drafts_pass_the_text_checks(self) -> None:
        from pack_checks import holds
        self.assertTrue(holds("Kind: post", {"kind": "post", "title": "", "text": ""}))
        self.assertFalse(holds("Kind: post", {"kind": "reply", "title": "", "text": ""}))
        self.assertIn("P-0001: disclosure", self.after("Writer", {"status": "held", "text": "Plan your week.<br>Free."}))

    # agent_team E34-S27 (EPIC-34 L-6): DMs leave the posts ledger; every DM reply waits for Jordi's Send.
    CHAT = {"id": "C-0001", "platform": "Reddit", "account": "u/jordimr", "who": "u/someone", "kind": "dm", "link": "https://www.reddit.com/chat/room/x", "started": "2026-11-01", "state": "open"}
    THEIRS = {"id": "M-0001", "chat": "C-0001", "at": "2026-11-01 10:00", "from": "them", "text": "does it work with Codex?", "status": "received"}
    OURS = {"id": "M-0002", "chat": "C-0001", "at": "2026-11-01 10:20", "from": "us", "persona": "Responder", "text": "Yes, it does.", "answers": "M-0001", "checks": "pass", "status": "draft"}

    def dm(self, by: str | None, chats: list[dict], msgs: list[dict]) -> str:
        self.repo.messages(chats, msgs)
        return "\n".join(self.repo.issues(by))

    def test_the_responder_writes_chats_and_drafts_but_never_sends_a_draft(self) -> None:
        self.assertEqual("", self.dm("Responder", [self.CHAT], [self.THEIRS, self.OURS]))
        self.repo.commit()
        sent = {**self.OURS, "result": "sent 2026-11-01 10:30 UTC"}
        self.assertIn("M-0002: illegal status change draft -> scheduled by Responder", self.dm("Responder", [self.CHAT], [self.THEIRS, {**self.OURS, "status": "scheduled"}]))
        self.assertIn("M-0002: illegal status change draft -> posted by Responder", self.dm("Responder", [self.CHAT], [self.THEIRS, {**sent, "status": "posted"}]))
        self.assertIn("M-0002: Responder may not write Feedback", self.dm("Responder", [self.CHAT], [self.THEIRS, {**self.OURS, "feedback": "Approved 2026-11-01"}]))
        self.assertIn("M-0002: send_approved: no approval from Jordi in feedback", self.dm("Jordi", [self.CHAT], [self.THEIRS, {**self.OURS, "status": "scheduled"}]))
        self.assertIn("stays draft", self.dm("Jordi", [self.CHAT], [self.THEIRS, {**self.OURS, "status": "scheduled"}]))
        approved = {**self.OURS, "status": "scheduled", "feedback": "Approved 2026-11-01 10:25 UTC"}
        self.assertEqual("", self.dm("Jordi", [self.CHAT], [self.THEIRS, approved]))
        self.repo.commit()
        self.assertIn("M-0002: Text may not change once scheduled", self.dm("Responder", [self.CHAT], [self.THEIRS, {**approved, "text": "Something else."}]))
        self.assertIn("M-0002: sent: no result", self.dm("Responder", [self.CHAT], [self.THEIRS, {**approved, "status": "posted"}]))
        self.assertEqual("", self.dm("Responder", [{**self.CHAT, "state": "waiting"}], [self.THEIRS, {**approved, "status": "posted", "result": "sent 2026-11-01 10:31 UTC, dry run first"}]))
        self.assertEqual("", self.dm("Jordi", [self.CHAT], [self.THEIRS, {**approved, "status": "draft"}]))  # Undo of Send before it went out

    def test_jordi_dont_send_undo_and_rewrite(self) -> None:
        self.dm("Responder", [self.CHAT], [self.THEIRS, self.OURS])
        self.repo.commit()
        self.assertEqual("", self.dm("Jordi", [self.CHAT], [self.THEIRS, {**self.OURS, "text": "My own words."}]))
        self.assertEqual("", self.dm("Jordi", [self.CHAT], [self.THEIRS, {**self.OURS, "status": "pulled"}]))
        self.repo.commit()
        self.assertIn("illegal status change pulled -> draft by Responder", self.dm("Responder", [self.CHAT], [self.THEIRS, self.OURS]))
        self.assertIn("illegal status change pulled -> scheduled by Jordi", self.dm("Jordi", [self.CHAT], [self.THEIRS, {**self.OURS, "status": "scheduled", "feedback": "Approved x"}]))
        self.assertEqual("", self.dm("Jordi", [self.CHAT], [self.THEIRS, self.OURS]))

    def test_a_chat_left_by_rule_is_its_own_row_and_only_jordi_reopens_or_closes_it(self) -> None:
        left = {**self.CHAT, "state": "left", "reason": "tax question, not about Zenod"}
        self.assertEqual("", self.dm("Responder", [left], [self.THEIRS]))
        self.repo.commit()
        self.assertIn("C-0001: illegal state change left -> done by Responder", self.dm("Responder", [{**left, "state": "done"}], [self.THEIRS]))
        self.assertIn("C-0001: illegal state change left -> open by Responder", self.dm("Responder", [{**left, "state": "open"}], [self.THEIRS]))
        self.assertEqual("", self.dm("Jordi", [{**left, "state": "open", "feedback": "Draft requested 2026-11-02 21:14 UTC"}], [self.THEIRS]))
        self.repo.commit()
        asked = {**left, "feedback": "Draft requested 2026-11-02 21:14 UTC"}
        self.assertEqual("", self.dm("Jordi", [{**asked, "feedback": asked["feedback"] + "; Draft request undone 2026-11-02 21:15 UTC"}], [self.THEIRS]))  # Undo of Draft a reply for me
        self.assertIn("illegal state change open -> waiting by Jordi", self.dm("Jordi", [{**asked, "state": "waiting"}], [self.THEIRS]))
        self.assertIn("illegal state change open -> hidden by Responder", self.dm("Responder", [{**asked, "state": "hidden"}], [self.THEIRS]))
        self.assertEqual("", self.dm("Jordi", [{**left, "state": "done", "feedback": "Done 2026-11-02 21:15 UTC"}], [self.THEIRS]))
        self.repo.commit()
        self.assertEqual("", self.dm("Jordi", [left], [self.THEIRS]))  # Undo of Done
        self.assertIn("C-0001: chat", "C-0001: chat")  # (ids are per table)
        self.assertIn("removed", self.dm("Responder", [], [self.THEIRS]))

    def test_a_dm_is_never_a_new_posts_row_and_old_ones_move(self) -> None:
        self.assertIn("P-0003: Community 'DM u/someone': a DM is not a post", self.after("Responder", {}, {"id": "P-0003", "kind": "reply", "status": "draft", "community": "DM u/someone", "text": "Hi"}))
        self.assertIn("P-0003: Community 'DMs': a DM is not a post", self.after(None, {}, {"id": "P-0003", "kind": "reply", "status": "draft", "community": "DMs", "text": "Hi"}))
        self.assertEqual("", self.after("Responder", {}, {"id": "P-0003", "kind": "reply", "status": "draft", "community": "r/other", "text": "Hi"}))
        moved = {"status": "moved", "result": "moved to data/messages-ledger.md C-0001"}
        self.assertEqual("", self.after("Delivery manager", moved))
        self.assertIn("P-0001: illegal status change draft -> moved by Writer", self.after("Writer", moved))
        self.assertIn("P-0001: Delivery manager may not write Text", self.after("Delivery manager", {**moved, "text": "x"}))
        self.repo.commit()
        self.assertIn("illegal status change moved -> draft", self.after(None, {"status": "draft"}))

    def test_a_shifted_row_is_refused_format_word_and_body_in_text(self) -> None:
        # zenod-social P-0104/P-0105 (2026-11-04): a redraft wrote the title in Text and the body in Format, so the page showed no post.
        body = "One thing sped up my dev. · A central memory sits under it. · How do you hand work to agents?"
        shifted = {"title": "Old title", "text": "How I hand work to agents now (r/LLMDevs discussion; E11-S8, L-6)", "format": body}
        out = self.after("Writer", shifted)
        self.assertIn("P-0001: Format 'One thing sped up my dev.", out)
        self.assertIn("P-0001: Text 'How I hand work to agents now (r/LLMDevs discussion; E11-S8,': Text reads like a title", out)
        self.assertIn("Format", self.after("Writer", {"format": "x" * 41}))
        self.assertEqual("", self.after("Writer", {"title": "How I hand work to agents now (r/LLMDevs discussion; E11-S8)", "text": body, "format": "text"}))
        self.assertEqual("", self.after("Writer", {"text": "1/ a · 2/ b", "format": "thread (2 posts)"}))
        self.assertEqual("", self.after("Writer", {"format": "demo clip"}))

    def test_a_removed_row(self) -> None:
        self.repo.ledger({})
        self.assertIn("P-0002: row removed", "\n".join(self.repo.issues()))

    def test_reply_rows_start_at_draft_and_go_live_with_checks(self) -> None:
        reply = {"id": "P-0003", "kind": "reply", "status": "posted", "link": "https://x.y/r", "text": "Thanks!"}
        self.assertEqual("", self.after("Responder", {}, reply))  # a reply in our own thread: no disclosure needed
        self.assertIn("P-0003: link_present", self.after("Responder", {}, {**reply, "link": ""}))
        outreach = {**reply, "kind": "outreach", "persona": "Engager"}
        self.assertIn("P-0003: disclosure", self.after("Engager", {}, outreach))
        self.assertEqual("", self.after("Engager", {}, {**outreach, "platform": "X"}))

    # agent_team E64-S4: ideas never expire; one idea becomes a post per platform; it closes only parked or spent.
    def test_an_idea_stays_open_across_platforms_and_closes_only_spent_or_parked(self) -> None:
        ideas = self.repo.root / "data/ideas.md"
        head = ideas.read_text()

        def rows(by: str, *states: str) -> str:
            ideas.write_text(head + "".join(f"| I-{n} | 2026-10-27 | idea {n} | text | Reddit, X | Scout | | {s} | |\n" for n, s in enumerate(states, 1)))
            return "\n".join(self.repo.issues(by))

        rows("Scout", "new", "new", "drafted", "posted")
        self.repo.commit()
        self.assertEqual("", rows("Writer", "open", "spent", "open", "open"))  # legacy drafted/posted read as open
        self.repo.commit()
        self.assertEqual("", rows("Jordi", "parked", "spent", "open", "open"))
        self.assertIn("I-2: illegal state change spent -> open by Writer", rows("Writer", "open", "open", "open", "open"))
        self.assertIn("I-1: illegal state change open -> spent by Jordi", rows("Jordi", "spent", "spent", "open", "open"))
        # the same idea on two platforms: two post rows, both valid
        self.assertEqual("", self.after("Writer", {"idea": "I-1"}, {"id": "P-0003", "platform": "X", "idea": "I-1", "community": ""}))

    # zenod-social EPIC-11-A2: a dropped idea goes to the rejected pile (Why keeps the lesson); only Jordi undoes it.
    def test_a_dropped_idea_is_rejected_and_only_jordi_takes_it_back(self) -> None:
        ideas = self.repo.root / "data/ideas.md"
        head = ideas.read_text()

        def rows(by: str, *states: str) -> str:
            ideas.write_text(head + "".join(f"| I-{n} | 2026-10-27 | idea {n} | text | Reddit | Scout | | {s} | |\n" for n, s in enumerate(states, 1)))
            return "\n".join(self.repo.issues(by))

        rows("Scout", "new", "new", "new")
        self.repo.commit()
        self.assertEqual("", rows("Writer", "rejected", "open", "parked"))
        self.repo.commit()
        self.assertEqual("", rows("Writer", "rejected", "rejected", "rejected"))  # open and parked -> rejected
        self.repo.commit()
        self.assertIn("I-1: illegal state change rejected -> open by Writer", rows("Writer", "open", "rejected", "rejected"))
        self.assertIn("I-1: illegal state change rejected -> epic by Jordi", rows("Jordi", "epic", "rejected", "rejected"))
        self.assertEqual("", rows("Jordi", "open", "rejected", "rejected"))  # Jordi's undo

    def test_the_scout_may_not_reject_an_idea(self) -> None:
        ideas = self.repo.root / "data/ideas.md"
        head = ideas.read_text()
        ideas.write_text(head + "| I-1 | 2026-10-27 | idea 1 | text | Reddit | Scout | | new | |\n")
        self.repo.commit()
        ideas.write_text(head + "| I-1 | 2026-10-27 | idea 1 | text | Reddit | Scout | | rejected | |\n")
        self.assertIn("I-1: illegal state change new -> rejected by Scout", "\n".join(self.repo.issues("Scout")))

    # agent_team E64-S6: a reply in someone else's thread waits for Jordi when the brief holds outreach (R4 `Kind: outreach`).
    def test_outreach_held_by_a_hold_rule_goes_out_only_after_jordis_approve(self) -> None:
        brief = self.repo.root / "data/brief.md"
        r1 = '| R1 | mentions "pricing" | Jordi answers pricing himself |\n'
        brief.write_text(brief.read_text().replace(r1, r1 + "| R4 | Kind: outreach | Jordi approves every thread reply |\n"))
        self.repo.commit()
        out = {"id": "P-0003", "kind": "outreach", "persona": "Engager", "platform": "X", "community": "@someone", "text": "I build Zenod, so biased: we check the evidence link."}
        self.assertIn("P-0003: hold_rules_outreach: matches hold rule R4", self.after("Engager", {}, {**out, "status": "posted", "link": "https://x.com/a/1"}))
        self.assertEqual("", self.after("Engager", {}, {**out, "status": "held"}))
        self.repo.commit()
        self.assertIn("P-0003: approved", self.after("Jordi", {}, {**out, "status": "scheduled"}))
        self.assertEqual("", self.after("Jordi", {}, {**out, "status": "scheduled", "feedback": "Approved 2026-11-03"}))
        self.repo.commit()
        self.assertEqual("", self.after("Engager", {}, {**out, "status": "posted", "feedback": "Approved 2026-11-03", "link": "https://x.com/a/1"}))
        self.assertEqual("", self.after("Engager", {}, {**out, "status": "expired", "feedback": "Approved 2026-11-03"}))  # cooled
        self.assertIn("P-0003: illegal status change scheduled -> posted by Writer", self.after("Writer", {}, {**out, "status": "posted", "feedback": "Approved 2026-11-03", "link": "https://x.com/a/1"}))

    def table(self, rel: str, sec: dict, rows: list[dict], heading: str | None = None) -> None:
        cols = [(k, f["column"]) for k, f in sec["fields"].items() if "computed" not in f]
        p = self.repo.root / rel
        lines = [f"# {Path(rel).stem}", ""] if heading is None or not p.is_file() else []
        lines += ([f"## {heading}", ""] if heading else []) + ["| " + " | ".join(c for _, c in cols) + " |", "|" + "---|" * len(cols)]
        lines += ["| " + " | ".join(r.get(k, "") for k, _ in cols) + " |" for r in rows]
        return "\n".join(lines) + "\n"

    # agent_team E64-S5: the Reporter writes insights and proposes My calls; only Jordi accepts a call; nothing is deleted.
    def test_the_reporter_writes_insights_and_only_jordi_accepts_a_call(self) -> None:
        secs = SOCIAL["files"]["insights"]["sections"]
        line = {"id": "IN-1", "insight": "Questions draw comments", "use": "End on a question", "evidence": "P-0019", "confidence": "medium · 4 posts", "since": "2026-11-03", "state": "active"}
        call = {"id": "MC-1", "call": "Shorter, end on the question", "evidence": "P-0053 2026-11-01, P-0060 2026-11-02", "since": "2026-11-03", "state": "proposed"}

        def write(by: str, lines: list[dict], calls: list[dict]) -> str:
            (self.repo.root / "data/insights.md").write_text("# Insights\n\n" + self.table("x", secs["lines"], lines, "Insights") + "\n" + self.table("x", secs["calls"], calls, "Proposed calls"))
            return "\n".join(self.repo.issues(by))

        self.assertIn("IN-1: Writer may not add rows", write("Writer", [line], [call]))
        self.assertEqual("", write("Reporter", [line], [call]))
        self.repo.commit()
        self.assertIn("MC-1: illegal state change proposed -> accepted by Reporter", write("Reporter", [line], [{**call, "state": "accepted"}]))
        self.assertEqual("", write("Jordi", [line], [{**call, "state": "accepted"}]))
        self.assertEqual("", write("Reporter", [{**line, "state": "retired"}], [call]))
        self.assertIn("IN-1: row removed", write("Reporter", [], [call]))

    def test_threads_are_kept_the_scout_watches_and_the_engager_answers(self) -> None:
        sec = SOCIAL["files"]["threads"]["sections"]["rows"]
        th = {"id": "TH-1103-1", "found": "2026-11-03T08:00Z", "platform": "Reddit", "community": "r/ClaudeCode", "title": "t", "link": "https://www.reddit.com/r/ClaudeCode/comments/x/", "why": "message 1", "numbers": "31 comments", "visibility": "8.2", "state": "watch"}

        def write(by: str, *rows: dict) -> str:
            (self.repo.root / "data/threads.md").write_text(self.table("data/threads.md", sec, list(rows)))
            return "\n".join(self.repo.issues(by))

        self.assertIn("TH-1103-1: Engager may not add rows", write("Engager", th))
        self.assertEqual("", write("Scout", th))
        self.repo.commit()
        self.assertEqual("", write("Engager", {**th, "state": "drafted", "reply": "P-0002"}))
        self.assertIn("TH-1103-1: illegal state change watch -> drafted by Scout", write("Scout", {**th, "state": "drafted"}))
        self.assertIn("TH-1103-1: row removed", write("Scout"))

    def test_converting_an_old_ledger_compares_no_rows(self) -> None:
        old = self.repo.root / "data/posts-ledger.md"
        old.write_text("# Posts ledger\n\n| Date | Persona | Platform | Link | Title | Status | Replies | Result |\n"
                       "|---|---|---|---|---|---|---|---|\n| 2026-10-25 | Responder | Reddit (reply) | x | t | posted | 0 | ok |\n")
        self.repo.commit()
        self.assertEqual("", self.after(None, {"id": "P-0003", "kind": "reply", "status": "posted", "text": "Thanks!"}))
        self.assertIn("Status 'left for Jordi' not one of", self.after(None, {"status": "left for Jordi"}))
        self.repo.commit()
        self.assertIn("P-0001: row removed", self.after(None))


class InitAndHook(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory(prefix="epicspine-pack-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def test_init_writes_the_product_deck_with_its_eight_parts(self) -> None:
        # agent_team E78-S1: a deterministic place for the product in every campaign repo.
        (self.root / "AGENTS.md").write_text("# AGENTS\n")
        pack_init.init(self.root, "social")
        deck = (self.root / "data/product.md").read_text()
        for h in ("Why it exists", "Who it is for", "How it works", "What it does for you", "What is included", "How much it costs", "How you get it", "How it differs"):
            self.assertIn(f"## {h}\n", deck)

    def test_init_twice_is_a_no_op_and_never_overwrites(self) -> None:
        (self.root / "data").mkdir()
        (self.root / "data/brief.md").write_text("# Brief\n\n## Voice\n\n- plain\n")
        (self.root / "AGENTS.md").write_text("# AGENTS\n\nIntegration policy: main-direct\n")
        self.assertTrue(pack_init.init(self.root, "social"))
        house = (self.root / "data/brief.md").read_text()
        self.assertTrue(house.startswith("# Brief\n\n## Voice\n\n- plain\n"))
        self.assertEqual(1, house.count("## Voice\n"))
        # E64-S13: one root brief file holds the brief and the directions sections; the old files are never made
        for heading in ("## Never say", "## Points to emphasize", "## Feedback log", "## Hold for me", "## Week", "## Month"):
            self.assertEqual(1, house.count(heading + "\n"), heading)
        self.assertFalse((self.root / "data/message-house.md").exists())
        self.assertFalse((self.root / "data/directions.md").exists())
        self.assertEqual(["social"], pack.enabled(self.root))
        before = snapshot(self.root)
        self.assertEqual([], pack_init.init(self.root, "social"))
        self.assertEqual(before, snapshot(self.root))
        self.assertEqual([], pack_validate.run(self.root, False))

    def test_an_old_message_house_warns_but_fails_no_commit(self) -> None:
        # agent_team E64-S13: data/message-house.md was folded into data/brief.md; a repo still holding it is told, never blocked
        (self.root / "AGENTS.md").write_text("# AGENTS\n\nPack: social\n")
        pack_init.init(self.root, "social")
        (self.root / "data/message-house.md").write_text("# Message house\n\n## Voice\n\n- plain\n")
        self.assertEqual([], pack_validate.run(self.root, False))
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, pack_validate.main(["--repo", str(self.root)]))
        self.assertIn("warning: pack social: data/message-house.md: folded into data/brief.md (agent_team E64-S13); move its sections", err.getvalue())

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

    def test_commit_hook_refuses_a_responder_commit_that_sends_its_own_dm_draft(self) -> None:
        # agent_team E34-S27: the approval rule by mechanism (root L-12): a Responder commit moving its DM draft to
        # scheduled (or straight to posted) is refused; Jordi's Send with his Approved note passes.
        git = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]
        subprocess.run(["git", "init", "-q"], cwd=self.root, env=safe_env())
        pack_init.init(self.root, "social")
        repo = Repo.__new__(Repo)
        repo.root = self.root
        chat = Validate.CHAT
        repo.messages([chat], [Validate.THEIRS, Validate.OURS])
        subprocess.run([*git, "add", "-A"], cwd=self.root, env=safe_env())
        subprocess.run([*git, "commit", "-qm", "base", "--no-verify"], cwd=self.root, env=safe_env())
        hook = lambda by: subprocess.run([sys.executable, "-B", str(SCRIPTS / "pre_commit.py")], cwd=self.root, capture_output=True, text=True, env=safe_env(EPICSPINE_PERSONA=by))  # noqa: E731
        for status in ("scheduled", "posted"):
            repo.messages([chat], [Validate.THEIRS, {**Validate.OURS, "status": status, "result": "sent", "feedback": ""}])
            subprocess.run([*git, "add", "-A"], cwd=self.root, env=safe_env())
            bad = hook("Responder")
            self.assertEqual(1, bad.returncode, status)
            self.assertIn(f"M-0002: illegal status change draft -> {status} by Responder", bad.stderr)
        repo.messages([chat], [Validate.THEIRS, {**Validate.OURS, "status": "scheduled", "feedback": "Approved 2026-11-02 21:30 UTC"}])
        subprocess.run([*git, "add", "-A"], cwd=self.root, env=safe_env())
        good = hook("Jordi")
        self.assertEqual(0, good.returncode, good.stderr)

    def test_cli(self) -> None:
        run = lambda *a: subprocess.run([sys.executable, "-B", str(SCRIPTS / "pack.py"), *a], capture_output=True, text=True, env=safe_env())  # noqa: E731
        self.assertIn("AGENTS.md: added Pack: social", run("init", "social", "--repo", str(self.root)).stdout)
        self.assertIn("nothing to do", run("init", "social", "--repo", str(self.root)).stdout)
        done = run("validate", "--repo", str(self.root))
        self.assertEqual((0, "ok (social)\n"), (done.returncode, done.stdout))


if __name__ == "__main__":
    unittest.main()
