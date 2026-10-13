#!/usr/bin/env python3
"""Minimal shell lexer for the manager guard: split a command into simple
commands, each ``(words, redirects, heredoc body)``. Handles quotes, escapes,
``$(...)``/backticks (their inner commands become extra segments), comments,
heredocs and redirections. Not a full shell parser; good enough to classify.
Stdlib only, Python 3.10+.
"""

from __future__ import annotations

import re

HEREDOC = re.compile(r"(?<!<)<<(?!<)-?\s*(['\"]?)([\w.-]+)\1")
REDIR = re.compile(r"&>>?|<<<|<<-?|<&|<>|<|>>|>&|>\||>")


def _grab(cmd: str, i: int) -> tuple[str, int]:
    """Inner text of the $(...) or `...` starting at ``i`` and the index after it."""
    if cmd[i] == "`":
        j = cmd.find("`", i + 1)
        j = len(cmd) if j < 0 else j
        return cmd[i + 1:j], j + 1
    depth, j = 1, i + 2
    while j < len(cmd) and depth:
        if cmd[j] == "\\":
            j += 2
            continue
        if cmd[j] == "'":
            k = cmd.find("'", j + 1)
            j = len(cmd) if k < 0 else k + 1
            continue
        depth += (cmd[j] == "(") - (cmd[j] == ")")
        j += 1
    return cmd[i + 2:j - 1], j


def lex(cmd: str) -> list[tuple[list[str], list[tuple[str, str]], str | None]]:
    """Split a shell command into (words, redirects, heredoc body) per simple command."""
    lines, kept, bodies, i = cmd.split("\n"), [], [], 0
    while i < len(lines):
        kept.append(lines[i])
        i += 1
        for m in HEREDOC.finditer(kept[-1]):
            start = i
            while i < len(lines) and lines[i].strip() != m.group(2):
                i += 1
            bodies.append("\n".join(lines[start:i]))
            i += 1
    cmd = "\n".join(kept)
    segs: list = []
    st = {"words": [], "redirs": [], "body": None, "buf": [], "has": False, "pending": None}

    def end_word() -> None:
        if st["has"]:
            word = "".join(st["buf"])
            if st["pending"]:
                st["redirs"].append((st["pending"], word))
                st["pending"] = None
            else:
                st["words"].append(word)
        st["buf"], st["has"] = [], False

    def end_seg() -> None:
        end_word()
        if st["words"] or st["redirs"]:
            segs.append((st["words"], st["redirs"], st["body"]))
        st.update(words=[], redirs=[], body=None)

    i, n = 0, len(cmd)
    while i < n:
        c = cmd[i]
        if c == "\\":
            st["buf"].append(cmd[i + 1:i + 2])
            st["has"], i = True, i + 2
        elif c == "'":
            j = cmd.find("'", i + 1)
            j = n if j < 0 else j
            st["buf"].append(cmd[i + 1:j])
            st["has"], i = True, j + 1
        elif c == '"':
            j = i + 1
            while j < n and cmd[j] != '"':
                if cmd[j] == "\\":
                    st["buf"].append(cmd[j + 1:j + 2])
                    j += 2
                elif cmd.startswith("$(", j) or cmd[j] == "`":
                    inner, j = _grab(cmd, j)
                    segs.extend(lex(inner))
                    st["buf"].append("$()")
                else:
                    st["buf"].append(cmd[j])
                    j += 1
            st["has"], i = True, j + 1
        elif cmd.startswith("$(", i) or c == "`":
            inner, i = _grab(cmd, i)
            segs.extend(lex(inner))
            st["buf"].append("$()")
            st["has"] = True
        elif c == "#" and not st["has"]:
            j = cmd.find("\n", i)
            i = n if j < 0 else j
        elif c in " \t":
            end_word()
            i += 1
        elif c in "<>" or cmd.startswith("&>", i):
            if st["has"] and "".join(st["buf"]).isdigit():
                st["buf"], st["has"] = [], False
            end_word()
            op = REDIR.match(cmd, i).group(0)
            i += len(op)
            if op in ("<<", "<<-") and bodies:
                st["body"] = bodies.pop(0)
            st["pending"] = op
        elif c in ";&|\n()":
            end_seg()
            i += 1
        else:
            st["buf"].append(c)
            st["has"], i = True, i + 1
    end_seg()
    return segs
