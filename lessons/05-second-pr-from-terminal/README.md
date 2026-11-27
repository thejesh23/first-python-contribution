# Lesson 05: Your second PR, from the terminal

**Time:** 7 minute video · 30 minute exercise
**You'll need:** a green `tools/doctor.py` (Lesson 03)

This time you'll contribute like you would to a real Python project: on a
branch, from the terminal, with **code and a test**, checked by CI before
it's merged.

You'll add two files. In this lesson our example learner is `ada-lovelace`;
use your own username.

| File | What's in it |
|---|---|
| `practice/greetings/ada_lovelace.py` | A function, `greet(name)`, that returns a greeting |
| `practice/tests/test_ada_lovelace.py` | A test that checks it |

**Your module name** is your GitHub username in lowercase, with `-`
replaced by `_`: `Ada-Lovelace` becomes `ada_lovelace`. Python can't import a
module with a hyphen in its name. (If your username starts with a digit, put
`u_` in front: `42cats` becomes `u_42cats`. The bot tells you the exact name
if you get it wrong.)

## Step 1: Start from the latest upstream

```bash norun
cd first-python-contribution
git fetch upstream
```

(Commands in this lesson are marked as not run in CI because they need your
fork.) `git fetch` downloads the original repo's newest commits without
changing your files. You start your branch from them in Step 3.

## Step 2: Make a virtual environment

A **virtual environment** ("venv") is a private Python just for this project.
Whatever you install in it can't clash with other projects. Almost every
Python project's CONTRIBUTING file starts with this step.

```bash norun
python3 -m venv .venv
source .venv/bin/activate
python -m pip install pytest ruff
```

On Windows (Git Bash) the middle line is `source .venv/Scripts/activate`.

Your prompt now starts with `(.venv)`. That means the venv is active, and
`python` now means the venv's Python. Open a new terminal later? Run the
`source` line again. The `.venv` folder is listed in `.gitignore`, so git
never commits it.

- **pytest** runs tests.
- **ruff** checks and formats code so it matches the project's style.

## Step 3: Make a branch

```bash norun
git switch -c exercise-2 upstream/main
```

`upstream/main` is the original repo's newest commit, as you just fetched
it. **Always start new work from there**, not from your own `main`: your
`main` still holds your first commit from Lesson 02, which may not be merged
yet, and it would come along into this pull request. One branch per pull
request, one change per branch. Never work on `main` directly.

## Step 4: Write the test first

Create `practice/tests/test_ada_lovelace.py` in your editor:

```python
from greetings.ada_lovelace import greet


def test_greet_includes_name():
    assert "Sam" in greet("Sam")
```

A test is a function whose name starts with `test_`. `assert` says "this
must be true". Run it:

```bash norun
python -m pytest practice
```

It fails, and that's the point:

```text
E   ModuleNotFoundError: No module named 'greetings.ada_lovelace'
=========================== short test summary info ============================
ERROR practice/tests/test_ada_lovelace.py
```

The test can't find your function because you haven't written it yet.
Seeing a test fail first proves it actually tests something.

## Step 5: Write the function

Create `practice/greetings/ada_lovelace.py`:

```python
"""Greeting for ada-lovelace."""


def greet(name: str) -> str:
    """Return a friendly greeting for name."""
    return f"Hello, {name}! Welcome to open source."
```

- The text in triple quotes is a **docstring**: it says what the module or function is for.
- `name: str` and `-> str` are **type hints**: `name` is a string, and so is the result.
- The `f"..."` is an **f-string**: `{name}` is replaced by the value of `name`.

Change the message if you like. It must include the name, fit on one line
and be at most 120 characters. Run the tests again:

```bash norun
python -m pytest practice
```

```text
practice/tests/test_ada_lovelace.py .                                    [ 12%]
practice/tests/test_all_greetings.py ...                                 [ 50%]
practice/tests/test_textkit.py .                                         [ 62%]
practice/tests/test_thejesh23.py ...                                     [100%]

============================== 8 passed in 0.01s ===============================
```

Each `.` is a passing test. `test_all_greetings.py` is the course's own test:
it checks every learner's `greet` follows the rules, including yours. Your
list is longer and your number is higher: every learner adds a test file.

## Step 6: Format and lint

```bash norun
ruff format practice
ruff check practice
```

`ruff format` rewrites your files to the project's style (spacing, quotes,
blank lines). `ruff check` looks for mistakes like unused imports. You want:

```text
All checks passed!
```

CI runs exactly these three commands. If they pass on your computer, they'll
pass in CI.

## Step 7: Commit

```bash norun
git status
git add practice/greetings/ada_lovelace.py practice/tests/test_ada_lovelace.py
git commit -m "Add exercise 2 greeting for ada-lovelace"
```

`git status` should show only your two new files. Add exactly those. (If
you see `.venv/` listed, your `.gitignore` is missing: check that you made
the branch from `upstream/main` in Step 3.)

## Step 8: Push your branch to your fork

```bash norun
git push -u origin exercise-2
```

`-u` remembers that this branch goes to `origin`, so next time a plain
`git push` is enough.

## Step 9: Open the pull request

```bash norun
gh repo set-default thejesh23/first-python-contribution
gh pr create --fill
```

`set-default` tells gh which repo your pull requests go to (you only do it
once). `--fill` uses your commit message as the title. gh prints the link
to your new PR. That's fine for this exercise; for a real project,
Lesson 11 shows how to write a title and description that get reviewed.

Prefer the browser? Open your fork on GitHub and click **Compare & pull request**.

## Step 10: Watch CI

```bash norun
gh pr checks --watch
```

One check runs on your PR: **Exercise 2 tests** (listed as `test`). It
runs `ruff format --check`, `ruff check` and `pytest` on your code, exactly
like Steps 5 and 6.

> **No checks yet?** GitHub doesn't run a newcomer's checks until a
> maintainer approves them. If your Lesson 02 pull request isn't merged
> (you skipped it, or the bot is still waiting for a fix), this check waits
> too: `gh pr checks` says `no checks reported on the 'exercise-2' branch`,
> and the pull request page says a workflow is awaiting approval. Two ways
> out:
>
> - Finish Lesson 02. Once that pull request is merged, push any new commit
>   to this branch (Stretch 1 in the exercise is a good one). The check
>   then starts by itself. The run that was held does not restart on its
>   own.
> - Or wait: a maintainer approves the held run, usually within a day.

When it finishes, a separate review bot checks your file names and that your
code only contains what it should. It doesn't appear in the checks list:
about a minute later it **comments** on your PR. If everything passed, a
maintainer reviews your PR and merges it.

Read the bot's comment with:

```bash norun
gh pr view --comments
```

## When a test fails

Suppose you changed the greeting to start with "Hi" but your test expects
"Hello". pytest shows you exactly what went wrong:

```text
    def test_greet_includes_name():
>       assert greet("Sam") == "Hello, Sam! Welcome to open source."
E       AssertionError: assert 'Hi, Sam! Wel... open source.' == 'Hello, Sam! ... open source.'
E
E         - Hello, Sam! Welcome to open source.
E         ?  ^^^^
E         + Hi, Sam! Welcome to open source.
E         ?  ^
```

Read it bottom up: `-` is what the test expected, `+` is what your function
returned, and `^` marks the difference. Fix the code (or the test), run
pytest again, commit, and `git push`. Your PR updates and CI runs again.
That fix-push-rerun loop is a normal part of every contribution.

## Step 11: Tidy up after the merge

```bash norun
git switch main
git pull upstream main
git branch -d exercise-2
```

`main` now includes your merged work, so the `exercise-2` branch can go.

If `git pull` says you have **divergent branches**, your Lesson 02 pull
request isn't merged yet. Leave `main` as it is and try again after the
merge. [Troubleshooting, section 8](../A-troubleshooting/#8-your-fork-is-out-of-date)
explains why.

Next: [Lesson 06: house rules](../06-house-rules/), the rules every project expects you to read first.
