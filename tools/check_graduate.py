"""Validate a capstone graduation pull request (Lesson 15).

The PR adds ``graduates/<login>.py``::

    name = "Ada Lovelace"
    github = "ada"
    pr = "https://github.com/OWNER/REPO/pull/123"
    message = "What I learned"

The file is parsed with :mod:`ast`, never executed. Then the linked pull
request is looked up on GitHub (with ``gh api``) and must be:

- merged
- opened by the learner
- merged by someone else (a maintainer)
- in a repository the learner doesn't own, that isn't a fork, and isn't this
  course or a practice repo

Usage (in CI)::

    python tools/check_graduate.py --login LOGIN --base BASE --head HEAD

Prints a Markdown comment; exits 0 if valid, 1 if not, 3 (silently) if the PR
doesn't add or change any ``graduates/<name>.py`` (a maintainer removing an
entry only deletes, so the bot stays quiet).
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_first_commit import LOGIN_RE, Result, _git, syntax_problem  # noqa: E402

FOLDER = "graduates"
REQUIRED = ("name", "github", "pr", "message")
MAX_LEN = {"name": 80, "github": 39, "pr": 200, "message": 280}
MAX_BYTES = 2_000
PR_RE = re.compile(r"^https://github\.com/([A-Za-z0-9-]+)/([A-Za-z0-9._-]+)/pull/(\d+)/?$")
NOT_A_LEARNER_PR = 3
PRACTICE_REPOS = {
    "thejesh23/first-python-contribution",
    "thejesh23/first-oss-contribution",
    "firstcontributions/first-contributions",
}


def is_learner_pr(paths: list[str]) -> bool:
    return any(p.startswith(f"{FOLDER}/") and p.count("/") == 1 and p.endswith(".py") for p in paths)


def check_changes(changes: list[tuple[str, str]], login: str) -> tuple[Result, str | None]:
    result = Result()
    expected = f"{FOLDER}/{login}.py"
    others = [p for _, p in changes if p.lower() != expected.lower()]
    if others:
        listed = ", ".join(f"`{p}`" for p in others[:5])
        result.errors.append(f"This pull request changes files other than `{expected}`: {listed}. Undo those changes.")
    mine = [(s, p) for s, p in changes if p.lower() == expected.lower()]
    if not mine:
        result.errors.append(f"Add a file named `{expected}` (your GitHub username).")
        return result, None
    status, path = mine[0]
    if status not in ("A", "M"):
        result.errors.append(f"`{path}` should be added or edited, not removed.")
        return result, None
    if path != expected:
        result.errors.append(f"Rename `{path}` to `{expected}` so the capital letters match your username.")
    return result, path


def parse_source(source: str) -> tuple[Result, dict[str, str]]:
    result = Result()
    values: dict[str, str] = {}
    if len(source.encode("utf-8")) > MAX_BYTES:
        result.errors.append(f"Your file is too long. Keep it under {MAX_BYTES} bytes.")
        return result, values
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        result.errors.append(f"Your file isn't valid Python: {syntax_problem(exc)}.")
        return result, values
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
            and node.targets[0].id in REQUIRED
            and node.targets[0].id not in values
        ):
            values[node.targets[0].id] = node.value.value.strip()
        else:
            result.errors.append(
                f'Line {node.lineno}: use only four lines like `name = "..."`: `name`, `github`, `pr` and `message`.'
            )
    for var in REQUIRED:
        value = values.get(var)
        if value is None:
            result.errors.append(f'`{var}` is missing. Add a line like `{var} = "..."`.')
        elif not value:
            result.errors.append(f"`{var}` is empty.")
        elif len(value) > MAX_LEN[var] or "\n" in value:
            result.errors.append(f"`{var}` must be one line of at most {MAX_LEN[var]} characters.")
    return result, values


def check_values(values: dict[str, str], login: str) -> Result:
    result = Result()
    gh = values.get("github", "")
    if gh and gh.lower() != login.lower():
        result.errors.append(f"`github` is `{gh}`, but this pull request was opened by `{login}`.")
    if values.get("pr") and not PR_RE.match(values["pr"]):
        result.errors.append("`pr` must be a GitHub pull request link like `https://github.com/OWNER/REPO/pull/123`.")
    return result


def check_pr_data(data: dict, login: str) -> Result:
    """Check the GitHub API's view of the linked pull request."""
    result = Result()
    repo = (data.get("base") or {}).get("repo") or {}
    full_name = repo.get("full_name", "")
    owner = (repo.get("owner") or {}).get("login", "")
    author = (data.get("user") or {}).get("login", "")
    merged_by = (data.get("merged_by") or {}).get("login", "")

    if full_name.lower() in PRACTICE_REPOS:
        result.errors.append(f"`{full_name}` is a practice repository. The capstone needs a real project.")
    if owner.lower() == login.lower():
        result.errors.append(f"`{full_name}` is your own repository. The capstone needs a project you don't own.")
    if repo.get("fork"):
        result.errors.append(f"`{full_name}` is a fork. Link the PR in the original project.")
    if author.lower() != login.lower():
        result.errors.append(f"That pull request was opened by `{author}`, not by you (`{login}`).")
    if not data.get("merged"):
        result.errors.append("That pull request isn't merged yet. Come back when it is. It's worth the wait!")
    elif merged_by and merged_by.lower() == login.lower():
        result.errors.append("You merged that pull request yourself. The capstone needs a maintainer to merge it.")
    return result


def fetch_pr(url: str) -> dict | None:
    m = PR_RE.match(url)
    if not m:
        return None
    owner, repo, number = m.groups()
    proc = subprocess.run(["gh", "api", f"repos/{owner}/{repo}/pulls/{number}"], capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    return json.loads(proc.stdout)


def validate(login: str, base: str, head: str, fetch=fetch_pr) -> Result:
    if not LOGIN_RE.match(login):
        return Result([f"Unexpected username `{login}`."])
    raw = _git("diff", "--no-renames", "--name-status", f"{base}...{head}")
    changes = [tuple(line.split("\t", 1)) for line in raw.splitlines() if line.strip()]
    result, path = check_changes(changes, login)  # type: ignore[arg-type]
    if path is None:
        return result
    parsed, values = parse_source(_git("show", f"{head}:{path}"))
    result.errors.extend(parsed.errors)
    result.errors.extend(check_values(values, login).errors)
    if result.ok:
        data = fetch(values["pr"])
        if data is None:
            result.errors.append(f"Couldn't find {values['pr']} on GitHub. Check the link.")
        else:
            result.errors.extend(check_pr_data(data, login).errors)
    return result


def format_comment(result: Result, login: str) -> str:
    if result.ok:
        return (
            f"🎓 Congratulations, @{login}! Your merged contribution checks out, so you're graduating. "
            "A maintainer will review this pull request, and once it's merged you'll appear "
            "on the graduates wall.\n\n"
            "You can contribute to any open source project now. Keep going, and pass it on: "
            "the best thing a graduate can do is help the next beginner."
        )
    lines = "\n".join(f"- {e}" for e in result.errors)
    return (
        f"Thanks, @{login}! Almost there:\n\n{lines}\n\n"
        "Fix your file in your fork and commit; this pull request updates by itself and is checked again."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a capstone graduation PR")
    parser.add_argument("--login", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    args = parser.parse_args(argv)
    if not is_learner_pr(
        _git("diff", "--no-renames", "--diff-filter=d", "--name-only", f"{args.base}...{args.head}").splitlines()
    ):
        return NOT_A_LEARNER_PR
    result = validate(args.login, args.base, args.head)
    print(format_comment(result, args.login))
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
