"""The content checks a pack's `checks` name, run on one row at the transitions it passed (pack_validate.py).

link_rule (max links, none on line n), disclosure (a phrase in the first lines), never_say (the brief's list),
hold_rules (a quoted phrase, or `field: value` (several joined by commas all match; `none` = empty), from the brief's hold table: matched means held, not scheduled), caps
(per platform: posts a day (threads_per_day, or threads_per_day_by_platform for that platform), posts per community a week (only on per_community_per_week_platforms, default Reddit; the account's own profile `u/<handle>` takes
profile_posts_per_day instead when the row's campaign brief names it, agent_team E60-S9), replies a day, counting rows in the live states), link_present,
approved (a phrase in a field only the owner writes: a held post goes out with Jordi's `Approved` note in its Feedback; a DM
reply with it in the message's Feedback), filled (a field is not empty: a sent DM reply records its send in Result)."""
from __future__ import annotations

import datetime as dt
import re

URL = re.compile(r"https?://\S+")
# A line break in a ledger cell: `<br>`, a literal `\n`, a newline, or the paragraph mark " · " the posts ledger joins
# paragraphs with (agent_team E61-S7: without it a whole post was line 1, so link_rule refused any link in it).
BREAK = re.compile(r"<br\s*/?>|\\n|\n|\s+·\s+", re.I)


# agent_team E60-S9: a Community cell that is the account's own Reddit profile (`u/jordimr`), as the console's ownHandle reads it.
PROFILE = re.compile(r"/?u/([\w-]{3,20})", re.I)


def profile_named(brief: str, handle: str) -> bool:
    """The campaign brief names the profile as a place it posts: one line with both `u/<handle>` and the word profile."""
    who = re.compile(rf"(?<![\w/])u/{re.escape(handle)}\b", re.I)
    return any(who.search(x) and re.search(r"\bprofile\b", x, re.I) for x in (brief or "").splitlines())


def brief_reader(repo, new):
    """code -> a campaign's brief: the `## Campaign plan` of the spine whose title is `# <code>: …`, read once (agent_team E60-S9)."""
    import pack_md as md
    briefs: dict[str, str] = {}

    def brief(code: str) -> str:
        code = (code or "").strip()
        if code and code not in briefs:
            briefs[code] = ""
            for sp in sorted(repo.glob("docs/spines/**/*.md")):
                text = new(str(sp.relative_to(repo))) or ""
                if re.match(rf"#\s+{re.escape(code)}\s*:", text):
                    briefs[code] = md.body(text, "Campaign plan") or ""
                    break
        return briefs.get(code, "")
    return brief


def lines(rec: dict) -> list[str]:
    return [x.strip() for x in BREAK.split(rec.get("text", "")) if x.strip()]


def day(rec: dict) -> str:
    return (rec.get("slot") or rec.get("date") or "")[:10]


def phrases(entry: str) -> list[str]:
    """Never-say phrases in one list item: its quoted parts, else the item itself."""
    quoted = re.findall(r'["“]([^"”]+)["”]', entry)
    return quoted or [entry.strip().rstrip(".").strip("`*")] if entry.strip().lower() not in ("none", "") else []


def holds(rule: str, rec: dict) -> bool:
    """A hold rule matches on a quoted phrase in title/text, or `field: value` (Platform: Reddit); free text is the Writer's call."""
    hay = f"{rec.get('title', '')} {rec.get('text', '')}".lower()
    quoted = re.findall(r'["“]([^"”]+)["”]', rule)
    if quoted:
        return any(q.lower() in hay for q in quoted)
    # `field: value`, or several joined by commas, all of which must match (agent_team E74-S5: `Kind: post, Campaign: EPIC-7`
    # holds one campaign's posts; the value `none` matches an empty or missing field, `Campaign: none` = the repo level).
    pairs = [re.fullmatch(r"\s*([\w ]+?)\s*[:=]\s*(.+?)\s*", part) for part in rule.split(",")]
    if not all(pairs):
        pairs = [re.fullmatch(r"\s*([\w ]+?)\s*[:=]\s*(.+?)\s*", rule)]
    def one(m: re.Match | None) -> bool:
        if not m:
            return False
        key, want = m.group(1).lower(), m.group(2).lower()
        have = str(rec.get(key) or "").strip().lower()
        return have == "" if want == "none" else key in rec and have == want
    return all(one(m) for m in pairs)


def run_check(key: str, c: dict, rec: dict, ctx: dict) -> list[str]:
    """A check's issues for one row; `fn` names the check it runs when its key is its own (send_approved runs approved)."""
    p, text, key = c.get("params", {}), lines(rec), c.get("fn", key)
    if key == "link_rule":
        out, links = [], URL.findall(rec.get("text", ""))
        if len(links) > p.get("max_links", len(links)):
            out.append(f"{len(links)} links in the text (max {p['max_links']})")
        n = p.get("no_link_on_line")
        return out + ([f"a link on line {n}"] if n and len(text) >= n and URL.search(text[n - 1]) else [])
    if key == "disclosure":
        head = " ".join(text[:p.get("within_lines", 2)]).lower().replace("’", "'")
        return [] if any(x.lower() in head for x in p.get("phrases", [])) else [
            f"no disclosure in the first {p.get('within_lines', 2)} lines (say one of: {', '.join(p.get('phrases', []))})"]
    if key == "never_say":
        hay = f"{rec.get('title', '')} {rec.get('text', '')}".lower()
        return [f"says never-say phrase {x!r}" for e in ctx["source"](c["source"]) for x in phrases(e) if x and x.lower() in hay]
    if key == "hold_rules":
        return [f"matches hold rule {r.get('id') or r.get('match')} ({r.get('match')}): it goes to held, not scheduled"
                for r in ctx["source"](c["source"]) if r.get("match") and holds(r["match"], rec)]
    if key == "benefit_named":
        rows = [r for r in ctx["source"](c["source"]) if r.get("id")]
        if not rows:
            return []  # a repo with no benefits home is not asked
        b = (rec.get("benefit") or "").strip()
        hit = next((r for r in rows if r["id"] == b), None)
        if not hit:
            return [f"names no benefit (Benefit: the number of one line in the brief's Benefits, {', '.join(r['id'] for r in rows)}): a post with none stays a draft"]
        return [] if (hit.get("status") or "").lower() == "works today" else [
            f"benefit {b} is {hit.get('status') or 'not marked works today'}: a post shows only a line that works today (call the others coming soon)"]
    if key == "approved":
        field, phrase = p.get("field", "feedback"), p.get("phrase", "approved")
        return [] if phrase.lower() in (rec.get(field) or "").lower() else [
            f"no approval from Jordi in {field} (his console Approve writes {phrase.capitalize()!r} there): it stays {p.get('stays', 'held')}"]
    if key == "filled":
        return [] if (rec.get(p.get("field", "result")) or "").strip() else [f"no {p.get('field', 'result')} (record it in the same commit)"]
    if key == "link_present":
        return [] if URL.match(rec.get(p.get("field", "link"), "")) else ["posted without its link (add it in the same commit)"]
    if key == "caps":
        plat, kind, out = rec.get("platform", "").lower(), rec.get("kind", "").lower(), []
        live = [r for r in ctx["rows"] if r.get(ctx["status"], "").lower() in ctx["live"] and r.get("platform", "").lower() == plat]
        posts = [r for r in live if r.get("kind", "").lower() == "post"]
        cap = (p.get("threads_per_day_by_platform") or {}).get(plat, p.get("threads_per_day", 1e9))
        # agent_team E86-S18 (Jordi via zenod-social EPIC-0-A27: "We should be doing multiple tweets every day in this
        # phase"): an account named in threads_per_day_by_account (`<platform>:<community>`, e.g. x:@zenodmemory) takes
        # its own day cap and counts only its own posts; every other account keeps the platform's cap, counted without them.
        own = {k.strip().lower(): v for k, v in (p.get("threads_per_day_by_account") or {}).items()}
        acct = lambda r: f"{plat}:{(r.get('community') or '').strip().lower()}"
        if acct(rec) in own:
            cap, mine, who = own[acct(rec)], [r for r in posts if acct(r) == acct(rec)], f"{rec.get('platform')} {rec.get('community')}"
        else:
            mine, who = [r for r in posts if acct(r) not in own], rec.get("platform")
        if kind == "post" and len(n := [r for r in mine if day(r) == day(rec)]) > cap:
            out.append(f"{len(n)} posts on {who} on {day(rec)} (cap {cap} a day)")
        try:
            week = dt.date.fromisoformat(day(rec)).isocalendar()[:2]
            same = [r for r in posts if r.get("community") and r.get("community") == rec.get("community")
                    and day(r) and dt.date.fromisoformat(day(r)).isocalendar()[:2] == week]
        except ValueError:
            same = []
        # a weekly cap per community only where communities exist (Reddit's subreddits), never on an account
        # handle like X's @ZenodAgent (agent_team E78-S5); a pack lists its community platforms
        community_platforms = [x.lower() for x in p.get("per_community_per_week_platforms", ["reddit"])]
        if kind == "post" and plat in community_platforms and len(same) > p.get("per_community_per_week", 1e9):
            # agent_team E60-S9 (Jordi 2026-11-10: "posting every day on Reddit what I accomplished"): the account's own
            # profile (Community `u/<handle>`) is not a community with its own rules: a campaign whose brief names it
            # gets one profile post a day there instead of one a week; the platform's day cap still counts it.
            prof = PROFILE.fullmatch((rec.get("community") or "").strip())
            if prof and profile_named(ctx.get("brief", lambda c: "")(rec.get("campaign", "")), prof.group(1)):
                if len(n := [r for r in same if day(r) == day(rec)]) > p.get("profile_posts_per_day", 1):
                    out.append(f"{len(n)} posts on the profile {rec.get('community')} on {day(rec)} (cap {p.get('profile_posts_per_day', 1)} a day)")
            else:
                out.append(f"{len(same)} posts in {rec.get('community')} that week (cap {p['per_community_per_week']} a week)"
                           + (f" (a daily profile post needs its campaign's brief to name the profile {rec.get('community')})" if prof else ""))
        if kind != "post" and len(n := [r for r in live if r.get("kind", "").lower() != "post" and day(r) == day(rec)]) > p.get("replies_per_day", 1e9):
            out.append(f"{len(n)} replies on {rec.get('platform')} on {day(rec)} (cap {p['replies_per_day']} a day)")
        return out
    return []
