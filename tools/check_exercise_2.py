"""Validate a learner's Exercise 2 pull request (Lesson 05).

The PR must add or edit exactly two files::

    practice/greetings/<module>.py      defines greet(name: str) -> str
    practice/tests/test_<module>.py     tests it

where ``<module>`` is the learner's GitHub username in lowercase with ``-``
replaced by ``_``. Both files are parsed with :mod:`ast`, never executed, and
must not import anything or call dangerous built-ins. The tests themselves run
in the read-only "Exercise 2 tests" workflow; its result is passed in here.

One more file is accepted: the learner's own ``first-commits/<login>.py``. A
branch made from the fork's ``main`` carries it along until the learner's
first pull request is merged. It gets the same checks as in that pull request.

Usage (in CI)::

    python tools/check_exercise_2.py --login LOGIN --base BASE --head HEAD --tests success --run-url URL

Prints a Markdown comment and exits 0 only if the PR is ready for a maintainer to merge. Exits 3,
printing nothing, when the PR isn't a learner's Exercise 2 PR at all (for
example a maintainer changing the course), so the bot stays quiet.
"""

from __future__ import annotations

import argparse
import ast
import keyword
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_first_commit import FOLDER as FIRST_COMMITS  # noqa: E402
from check_first_commit import LOGIN_RE, Result, _git, check_source, syntax_problem  # noqa: E402

MAX_BYTES = 3_000
BANNED_NAMES = {
    "__import__",
    "breakpoint",
    "compile",
    "eval",
    "exec",
    "getattr",
    "globals",
    "input",
    "locals",
    "open",
    "setattr",
    "delattr",
    "vars",
}


COURSE_FILES = {
    "practice/greetings/__init__.py",
    "practice/tests/test_all_greetings.py",
    "practice/tests/test_textkit.py",
}
NOT_A_LEARNER_PR = 3


def is_learner_pr(paths: list[str]) -> bool:
    """True if the PR touches at least one file shaped like a learner's exercise file."""
    for path in paths:
        if path in COURSE_FILES:
            continue
        parts = path.split("/")
        if len(parts) == 3 and parts[0] == "practice" and parts[2].endswith(".py"):
            if parts[1] == "greetings" or (parts[1] == "tests" and parts[2].startswith("test_")):
                return True
    return False


def module_name(login: str) -> str:
    """Turn a GitHub username into a valid Python module name."""
    name = login.lower().replace("-", "_")
    if name[0].isdigit():
        name = "u_" + name
    if keyword.iskeyword(name):
        name += "_"
    return name


def expected_paths(login: str) -> tuple[str, str]:
    mod = module_name(login)
    return f"practice/greetings/{mod}.py", f"practice/tests/test_{mod}.py"


def carried_first_commit(changes: list[tuple[str, str]], login: str) -> str | None:
    """The learner's own first-commit file, if this PR adds or edits it too.

    Lesson 02's commit sits on the fork's ``main``. Until that pull request is
    merged, a branch made from the fork's ``main`` brings the file along.
    """
    mine = f"{FIRST_COMMITS}/{login}.py"
    for status, path in changes:
        if path == mine and status in ("A", "M"):
            return path
    return None


def check_changes(changes: list[tuple[str, str]], login: str, existing: set[str] | None = None) -> Result:
    """Check which files the PR touches.

    ``existing`` is the set of the learner's two files present at the PR head
    (default: whatever the PR touches). A PR may change one or both files, as
    long as both exist afterwards.
    """
    result = Result()
    greet_path, test_path = expected_paths(login)
    wanted = {greet_path, test_path}
    touched = {path for _, path in changes}

    carried = carried_first_commit(changes, login)
    if carried:
        result.notes.append(
            f"This pull request also carries your first commit (`{carried}`), because your first pull "
            "request isn't merged yet and this branch started from your fork's `main`. That's fine here. "
            "Next time, start the branch from the original repo, as Lesson 05 shows: "
            "`git switch -c my-branch upstream/main`."
        )
    others = sorted(touched - wanted - {carried})
    if others:
        listed = ", ".join(f"`{p}`" for p in others[:5])
        result.errors.append(
            f"This pull request changes files other than your two exercise files: {listed}. "
            f"Only `{greet_path}` and `{test_path}` should change."
        )
    present = touched if existing is None else existing
    if not touched & wanted:
        result.errors.append(f"This pull request doesn't change `{greet_path}` or `{test_path}`.")
    for path in sorted(wanted - present):
        result.errors.append(f"Add `{path}`.")
    for status, path in changes:
        if path in wanted and status not in ("A", "M"):
            result.errors.append(f"`{path}` should be added or edited, not deleted.")
    return result


def _safety_errors(tree: ast.AST, label: str) -> list[str]:
    errors = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in BANNED_NAMES:
            errors.append(f"{label}, line {node.lineno}: `{node.id}` isn't allowed in this exercise.")
        elif isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            errors.append(f"{label}, line {node.lineno}: double-underscore attributes aren't allowed in this exercise.")
    return errors


def _parse(source: str, label: str, result: Result) -> ast.Module | None:
    if len(source.encode("utf-8")) > MAX_BYTES:
        result.errors.append(f"{label} is too long. Keep it under {MAX_BYTES} bytes.")
        return None
    try:
        return ast.parse(source)
    except SyntaxError as exc:
        result.errors.append(f"{label} isn't valid Python: {syntax_problem(exc)}.")
        return None


def _is_docstring(node: ast.stmt) -> bool:
    return isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)


def check_greeting(source: str) -> Result:
    result = Result()
    label = "Your greeting"
    tree = _parse(source, label, result)
    if tree is None:
        return result
    greet = None
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            result.errors.append(f"{label}, line {node.lineno}: no imports needed here. Remove it.")
        elif isinstance(node, ast.FunctionDef):
            if node.name == "greet":
                greet = node
        elif not _is_docstring(node):
            result.errors.append(f"{label}, line {node.lineno}: only functions (and a docstring) belong in this file.")
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)) and node not in tree.body:
            result.errors.append(f"{label}, line {node.lineno}: no imports needed here. Remove it.")
    if greet is None:
        result.errors.append(f"{label}: define a function `def greet(name: str) -> str:`.")
    else:
        args = greet.args
        if len(args.args) != 1 or args.vararg or args.kwarg or args.kwonlyargs:
            result.errors.append(f"{label}: `greet` should take exactly one argument, `name`.")
        elif not (isinstance(args.args[0].annotation, ast.Name) and args.args[0].annotation.id == "str"):
            result.errors.append(f"{label}: add a type hint: `def greet(name: str) -> str:`.")
        if not (isinstance(greet.returns, ast.Name) and greet.returns.id == "str"):
            result.errors.append(f"{label}: add a return type hint: `-> str`.")
    result.errors.extend(_safety_errors(tree, label))
    return result


def check_test(source: str, login: str) -> Result:
    result = Result()
    label = "Your test"
    mod = module_name(login)
    tree = _parse(source, label, result)
    if tree is None:
        return result
    imports_own = False
    tests = 0
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            if node.module == f"greetings.{mod}":
                imports_own = True
            elif node.module != "pytest":
                result.errors.append(
                    f"{label}, line {node.lineno}: import only from `greetings.{mod}` (or `pytest`), "
                    f"not `{node.module}`."
                )
        elif isinstance(node, ast.Import):
            if any(alias.name != "pytest" for alias in node.names):
                result.errors.append(f"{label}, line {node.lineno}: the only module you can import is `pytest`.")
        elif isinstance(node, ast.FunctionDef):
            tests += node.name.startswith("test_")
        elif not _is_docstring(node):
            result.errors.append(f"{label}, line {node.lineno}: only imports and test functions belong in this file.")
    if not imports_own:
        result.errors.append(f"{label}: import your function with `from greetings.{mod} import greet`.")
    if tests == 0:
        result.errors.append(f"{label}: add at least one function whose name starts with `test_`.")
    result.errors.extend(_safety_errors(tree, label))
    return result


def format_comment(result: Result, login: str, tests: str, run_url: str) -> str:
    tests_line = {
        "success": "✅ Your tests, ruff and the course's checks all passed.",
        "failure": f"❌ The tests or ruff failed. [Open the test run]({run_url}), "
        "scroll to the red ✘ step and read the last lines of its output.",
    }.get(tests, f"⚠️ The test run finished with `{tests}`. [Open it]({run_url}) to see why.")
    if result.ok and tests == "success":
        notes = "".join(f"\n\n{note}" for note in result.notes)
        return (
            f"🎉 Nice work, @{login}! {tests_line} A maintainer will review your pull "
            "request and merge it soon.\n\n"
            "You just did what real Python contributors do every day: write code, test it, "
            "pass CI and ask for review. Next up: Lesson 06, the house rules every project has."
            f"{notes}"
        )
    parts = [f"Thanks, @{login}! Not quite there yet:\n", tests_line]
    if result.errors:
        parts.append("\nThe bot also found:\n")
        parts.extend(f"- {e}" for e in result.errors)
    parts.append(
        "\nFix it on your branch, run `python -m pytest practice`, `ruff format practice` and "
        "`ruff check practice` again, then commit and `git push`. "
        "This pull request updates by itself and everything runs again."
    )
    return "\n".join(parts)


def _exists(rev: str, path: str) -> bool:
    return subprocess.run(["git", "cat-file", "-e", f"{rev}:{path}"], capture_output=True).returncode == 0


def validate(login: str, base: str, head: str) -> Result:
    if not LOGIN_RE.match(login):
        return Result([f"Unexpected username `{login}`."])
    raw = _git("diff", "--no-renames", "--name-status", f"{base}...{head}")
    changes = [tuple(line.split("\t", 1)) for line in raw.splitlines() if line.strip()]
    greet_path, test_path = expected_paths(login)
    existing = {p for p in (greet_path, test_path) if _exists(head, p)}
    result = check_changes(changes, login, existing)  # type: ignore[arg-type]
    if not result.ok:
        return result
    carried = carried_first_commit(changes, login)  # type: ignore[arg-type]
    if carried:
        problems = check_source(_git("show", f"{head}:{carried}"), login).errors
        result.errors.extend(f"Your first-commit file (`{carried}`): {problem}" for problem in problems)
    result.errors.extend(check_greeting(_git("show", f"{head}:{greet_path}")).errors)
    result.errors.extend(check_test(_git("show", f"{head}:{test_path}"), login).errors)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate an Exercise 2 pull request")
    parser.add_argument("--login", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--tests", required=True, help="conclusion of the Exercise 2 tests run")
    parser.add_argument("--run-url", default="")
    args = parser.parse_args(argv)
    if not is_learner_pr(
        _git("diff", "--no-renames", "--diff-filter=d", "--name-only", f"{args.base}...{args.head}").splitlines()
    ):
        return NOT_A_LEARNER_PR
    result = validate(args.login, args.base, args.head)
    print(format_comment(result, args.login, args.tests, args.run_url))
    return 0 if result.ok and args.tests == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
