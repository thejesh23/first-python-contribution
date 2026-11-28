"""Validate a learner's first-commit pull request.

The PR must add (or edit) exactly one file, ``first-commits/<login>.py``,
containing three string assignments: ``name``, ``github`` and ``message``.

The file is parsed with :mod:`ast` and never executed, so this is safe to run
on untrusted pull requests.

Usage (in CI)::

    python tools/check_first_commit.py --login LOGIN --base BASE_SHA --head HEAD_SHA

Prints a Markdown comment for the PR and exits 0 if the PR is valid, 1 if not.
A valid PR is merged by the workflow without a human reading it, so the rules
are strict: one ordinary file, three short strings, no links or mentions.
Exits 3, printing nothing, when the PR doesn't add or change any
``first-commits/<name>.py`` (for example a maintainer editing the folder's
README), so the bot stays quiet. It also stays quiet on an Exercise 2 pull
request that carries the learner's first commit along (their first pull
request isn't merged yet): ``check_exercise_2.py`` reviews that one.
"""

from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from dataclasses import dataclass, field

FOLDER = "first-commits"
REQUIRED = ("name", "github", "message")
MAX_BYTES = 2_000
MAX_LEN = {"name": 80, "github": 39, "message": 280}
LOGIN_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
LINK_RE = re.compile(r"https?://|www\.|@", re.IGNORECASE)  # nobody reads the file before it's merged
REGULAR_FILE = "100644"


NOT_A_LEARNER_PR = 3


def is_learner_pr(paths: list[str]) -> bool:
    """True if the PR touches at least one first-commits/<name>.py file."""
    return any(p.startswith(f"{FOLDER}/") and p.count("/") == 1 and p.endswith(".py") for p in paths)


@dataclass
class Result:
    errors: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)  # said in the comment, but not a problem

    @property
    def ok(self) -> bool:
        return not self.errors


def check_changes(changes: list[tuple[str, str]], login: str) -> tuple[Result, str | None]:
    """Check which files the PR touches.

    ``changes`` is a list of ``(status, path)`` pairs as printed by
    ``git diff --name-status`` (status ``A`` added, ``M`` modified, ...).
    Returns the result and the path of the learner's file if there is one.
    """
    result = Result()
    expected = f"{FOLDER}/{login}.py"

    if not changes:
        result.errors.append("This pull request doesn't change any files.")
        return result, None

    outside = [p for _, p in changes if p.lower() != expected.lower()]
    if outside:
        listed = ", ".join(f"`{p}`" for p in outside[:5])
        result.errors.append(
            f"This pull request changes files other than `{expected}`: {listed}. "
            "Your first commit should only add your own file. Undo the other "
            "changes in your fork."
        )

    mine = [(s, p) for s, p in changes if p.lower() == expected.lower()]
    if not mine:
        added_py = [p for s, p in changes if s == "A" and p.startswith(f"{FOLDER}/") and p.endswith(".py")]
        if added_py:
            result.errors.append(
                f"Your file is named `{added_py[0]}`, but it must be named after your GitHub username: `{expected}`."
            )
        else:
            result.errors.append(f"Add a file named `{expected}`.")
        return result, None

    status, path = mine[0]
    if status not in ("A", "M"):
        result.errors.append(f"`{path}` should be added or edited, not removed or renamed.")
        return result, None
    if path != expected:
        result.errors.append(
            f"Your file is `{path}`, but your username is spelled `{login}`. "
            f"Rename it to `{expected}` so the capital letters match."
        )
    return result, path


def syntax_problem(exc: SyntaxError) -> str:
    """ "unterminated string literal (line 3)": Python's message, with the line number said once."""
    message = re.sub(r"\s*\(detected at line \d+\)", "", str(exc.msg))
    return f"{message} (line {exc.lineno})"


def check_source(source: str, login: str) -> Result:
    """Check the contents of a learner's file without running it."""
    result = Result()

    if len(source.encode("utf-8")) > MAX_BYTES:
        result.errors.append(f"Your file is too long. Keep it under {MAX_BYTES} bytes.")
        return result

    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        hint = ' A missing quote `"` is the most common cause.' if "string" in str(exc.msg).lower() else ""
        result.errors.append(f"Your file isn't valid Python: {syntax_problem(exc)}.{hint}")
        return result

    values: dict[str, str] = {}
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            var = node.targets[0].id
            if var not in REQUIRED:
                result.errors.append(
                    f"Line {node.lineno}: unexpected variable `{var}`. Use only `name`, `github` and `message`."
                )
            elif var in values:
                result.errors.append(f"Line {node.lineno}: `{var}` is set twice.")
            else:
                values[var] = node.value.value
        else:
            result.errors.append(
                f'Line {node.lineno}: each line should look like `name = "text"`. '
                "Only three string variables are allowed: `name`, `github` and `message`."
            )

    for var in REQUIRED:
        if var not in values:
            result.errors.append(f'`{var}` is missing. Add a line like `{var} = "..."`.')

    for var, value in values.items():
        stripped = value.strip()
        if not stripped:
            result.errors.append(f"`{var}` is empty. Put some text between the quotes.")
        elif len(stripped) > MAX_LEN[var]:
            result.errors.append(f"`{var}` is too long ({len(stripped)} characters, maximum {MAX_LEN[var]}).")
        if "\n" in value or "\r" in value:
            result.errors.append(f"`{var}` must be on one line.")
        if var != "github" and LINK_RE.search(value):
            result.errors.append(f"`{var}` can't contain links or @mentions. Use plain words.")

    placeholder = {"name": "Your Name", "github": "your-github-username"}
    for var, text in placeholder.items():
        if values.get(var, "").strip() == text:
            result.errors.append(f"`{var}` still says `{text}`. Replace it with your own.")

    gh = values.get("github", "").strip()
    if gh and gh.lower() != login.lower() and gh not in placeholder.values():
        result.errors.append(f"`github` is `{gh}`, but this pull request was opened by `{login}`. They must match.")

    return result


def format_comment(result: Result, login: str) -> str:
    if result.ok:
        return (
            f"🎉 Looks great, @{login}! Your file passed every check, so I'm merging "
            "your pull request now.\n\n"
            "In a moment you'll see the purple **Merged** badge: your commit is then "
            "part of a public project. Next up: Lesson 03, setting up git on your "
            "own machine."
        )
    lines = "\n".join(f"- {e}" for e in result.errors)
    return (
        f"Thanks for your pull request, @{login}! A few things to fix first:\n\n"
        f"{lines}\n\n"
        "Fix them in your fork (open your file and click the ✏️ pencil, then "
        "commit). This pull request updates by itself and the check runs again. "
        "Stuck? Ask in a comment here and a maintainer will help."
    )


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def validate(login: str, base: str, head: str) -> Result:
    if not LOGIN_RE.match(login):
        return Result([f"Unexpected username `{login}`."])
    raw = _git("diff", "--no-renames", "--name-status", f"{base}...{head}")
    changes = [tuple(line.split("\t", 1)) for line in raw.splitlines() if line.strip()]
    result, path = check_changes(changes, login)  # type: ignore[arg-type]
    if path is None:
        return result
    mode = _git("ls-tree", head, "--", path).split(" ", 1)[0]
    if mode != REGULAR_FILE:
        result.errors.append(f"`{path}` must be an ordinary text file (not a link or a program).")
        return result
    source = _git("show", f"{head}:{path}")
    result.errors.extend(check_source(source, login).errors)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--login", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    args = parser.parse_args(argv)
    # Deleted files are left out: a maintainer removing an entry isn't a learner's PR, so the bot stays quiet.
    paths = _git("diff", "--no-renames", "--diff-filter=d", "--name-only", f"{args.base}...{args.head}").splitlines()
    if not is_learner_pr(paths):
        return NOT_A_LEARNER_PR
    from check_exercise_2 import is_learner_pr as is_exercise_2_pr  # imported here: that module imports this one

    if is_exercise_2_pr(paths):
        return NOT_A_LEARNER_PR  # an Exercise 2 PR carrying the first commit: the Exercise 2 bot reviews it
    result = validate(args.login, args.base, args.head)
    print(format_comment(result, args.login))
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
