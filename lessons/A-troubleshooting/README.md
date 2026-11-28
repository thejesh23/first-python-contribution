# Troubleshooting

**Time:** 2 minute video · as long as it takes

Something went wrong? Find the message you're seeing below. Each fix says
what happened and what to run. Nearly everything in git can be undone, so
don't panic, and **don't delete your folder and start again** until you've
read the fix.

| If you see... | Go to |
|---|---|
| `Support for password authentication was removed` / `Authentication failed` | [1. Login problems](#1-login-problems) |
| `Permission to OWNER/REPO.git denied` / `returned error: 403` | [2. Pushing to the wrong repo](#2-pushing-to-the-original-repo-instead-of-your-fork) |
| `Your local changes ... would be overwritten by checkout` | [3. Can't switch branches](#3-cant-switch-branches) |
| You committed on `main` by mistake | [4. Committed to main](#4-committed-to-main-by-mistake) |
| `! [rejected] ... (fetch first)` | [5. Push rejected](#5-push-rejected) |
| `tip of your current branch is behind its remote counterpart` | [5. Push rejected](#5-push-rejected) |
| `You are in 'detached HEAD' state` | [6. Detached HEAD](#6-detached-head) |
| Wrong files or message in your last commit | [7. Fix your last commit](#7-fix-your-last-commit) |
| `This branch has conflicts that must be resolved` | [Lesson 12](../12-ci-and-review/) |
| Your fork says "X commits behind" | [8. Fork out of date](#8-your-fork-is-out-of-date) |
| `fatal: Need to specify how to reconcile divergent branches` | [8. Fork out of date](#8-your-fork-is-out-of-date) |
| `nothing to commit, working tree clean` but you changed something | [9. Nothing to commit](#9-nothing-to-commit) |
| `error: externally-managed-environment` | [10. Python environment](#10-python-and-pip-problems) |
| `No module named pytest` / `command not found: pytest` | [10. Python environment](#10-python-and-pip-problems) |
| `python3: command not found` (Windows) | [10. Python environment](#10-python-and-pip-problems) |
| PR opened against your own fork | [11. PR in the wrong place](#11-pr-opened-in-the-wrong-place) |
| `.venv` or other junk in your PR | [12. Files that shouldn't be committed](#12-files-that-shouldnt-be-committed) |
| `refusing to allow an OAuth App to create or update workflow ... without workflow scope` | [13. Push refused: workflow scope](#13-push-refused-workflow-scope) |
| Checks say "awaiting approval" | [Lesson 12](../12-ci-and-review/) (just wait) |

**Practise the fixes safely:** sections 3–7 come with a sandbox that
reproduces each problem. Start it from any folder *outside* a real project:

```bash
git init -q --bare -b main practice-remote.git
git clone -q practice-remote.git trouble-sandbox
cd trouble-sandbox
echo 'print("hello")' > app.py
git add app.py
git commit -q -m "Add app.py"
git push -q origin main
```

## 1. Login problems

```text
remote: Support for password authentication was removed on August 13, 2021.
fatal: Authentication failed for 'https://github.com/...'
```

GitHub doesn't accept your account password for git. Log in with gh, and
let it handle git's credentials too:

```bash norun
gh auth login
gh auth setup-git
gh auth status
```

## 2. Pushing to the original repo instead of your fork

```text
remote: Permission to OWNER/REPO.git denied to YOUR-USERNAME.
fatal: unable to access '...': The requested URL returned error: 403
```

You cloned the **original** project, not your fork, so `origin` points
somewhere you can't push. Check:

```bash norun
git remote -v
```

If `origin` is `OWNER/REPO` rather than `YOUR-USERNAME/REPO`, fix it
without losing anything. From inside the folder:

```bash norun
gh repo fork --remote
git push -u origin my-branch
```

`gh repo fork --remote` creates your fork (if it doesn't exist), renames the
old `origin` to `upstream`, and adds your fork as `origin`.

## 3. Can't switch branches

```text
error: Your local changes to the following files would be overwritten by checkout:
	app.py
Please commit your changes or stash them before you switch branches.
Aborting
```

You have unsaved work, and switching branches would overwrite it. git
stopped to protect it. In the sandbox:

```bash
git switch -q -c experiment
echo 'print("experiment")' > app.py
git commit -q -am "Try an experiment"
git switch -q main
echo 'print("work in progress")' > app.py
```

```bash expect-fail
git switch experiment
```

Either commit the work, or **stash** it (put it aside), switch, and bring it
back later:

```bash
git stash
git switch experiment
git switch main
git stash pop
cat app.py
```

## 4. Committed to main by mistake

You meant to make a branch first, but committed on `main`. As long as you
**haven't pushed**, it's easy: make the branch *now* (it keeps your commit),
then put `main` back where it was.

```bash
git checkout -q -- app.py
git switch -q main
echo 'print("hello, world")' > app.py
git commit -q -am "Greet the world"
git branch greet-world
git reset --hard origin/main
git log --oneline greet-world -2
git switch greet-world
```

`git branch greet-world` makes a branch pointing at your commit.
`git reset --hard origin/main` moves `main` back. **`--hard` throws away
uncommitted changes**, so only run it once your work is safely on the new
branch. (In a fork, use `upstream/main` to match the original project.)

## 5. Push rejected

**"fetch first"** means GitHub has commits on your branch that you don't
have, for example a maintainer pushed a fix, or you applied a suggestion in
the browser:

```text
 ! [rejected]        main -> main (fetch first)
hint: Updates were rejected because the remote contains work that you do not
hint: have locally.
```

Bring their commits in under yours, then push:

```bash norun
git pull --rebase
git push
```

**"behind its remote counterpart"** after you rebased, amended or squashed
means you rewrote commits you'd already pushed (Lesson 12). That's expected:

```text
hint: Updates were rejected because the tip of your current branch is behind
hint: its remote counterpart.
```

```bash norun
git push --force-with-lease
```

If `--force-with-lease` is rejected too, someone else pushed in the
meantime: `git pull --rebase` first.

## 6. Detached HEAD

```text
You are in 'detached HEAD' state. You can look around, make experimental
changes and commit them, ...
```

You checked out a commit instead of a branch (for example with
`git checkout <hash>`). Nothing is broken. See it, and get back:

```bash
git checkout -q "$(git rev-parse HEAD)"
git status
git switch main
```

`git status` says `HEAD detached at ...` while you're detached.

If you made commits while detached and want to keep them, create a branch
right where you are **before** switching away:

```bash norun
git switch -c keep-my-work
```

## 7. Fix your last commit

Not pushed yet? Change the last commit freely:

Here a scratch file slipped into the commit, and the message is vague:

```bash
echo 'print("hello, open source")' > app.py
echo "my notes" > notes.txt
git add app.py notes.txt
git commit -q -m "Fixed stuff"
git reset --soft HEAD~1
git restore --staged notes.txt
git commit -q -m "Greet open source"
git log --oneline -1
git status --short
```

The new commit only has `app.py`, and `git status` shows `?? notes.txt`:
still on your computer, just not committed.

- `git reset --soft HEAD~1` undoes the last commit but keeps its changes staged.
- `git restore --staged FILE` takes a file out of the next commit (your
  edits stay).
- `git commit --amend` changes the last commit's message, or adds staged
  changes to it.

Already pushed? Same commands, then `git push --force-with-lease` (section 5).

## 8. Your fork is out of date

GitHub shows "This branch is X commits behind OWNER:main". Bring your fork's
`main` up to date:

```bash norun
git switch main
git pull upstream main
git push origin main
```

Or without touching your computer: `gh repo sync YOUR-USERNAME/REPO`, or the
**Sync fork** button on your fork's page.

If `git pull upstream main` stops with `Need to specify how to reconcile
divergent branches`, your `main` and the original's `main` each have commits
the other lacks.

**In this course**, that means your Lesson 02 pull request isn't merged yet:
its commit is on your `main`. Don't reset anything, because that pull
request is made from your fork's `main`. You don't need the pull: start new
work with `git fetch upstream` and `git switch -c my-branch upstream/main`,
as Lesson 05 does. After the merge, `git pull upstream main` works again.

**In a real project**, it's common after your PR was squash-merged. If your
fork's `main` has nothing you need and no open pull request is made from it,
reset it to match upstream:

```bash norun
git switch main
git fetch upstream
git reset --hard upstream/main
git push --force-with-lease origin main
```

## 9. Nothing to commit

```text
nothing to commit, working tree clean
```

git doesn't see your change. Usually one of:

- **The file isn't saved** in your editor.
- **You're in a different folder** or clone: check with `pwd` and `git remote -v`.
- **The file is ignored** by `.gitignore`: check with `git check-ignore -v FILE`.

## 10. Python and pip problems

```text
error: externally-managed-environment
```

You're installing into your system's Python (Homebrew and Linux Pythons
protect themselves). Use a virtual environment, as in Lesson 05:

```bash norun
python3 -m venv .venv
source .venv/bin/activate
python -m pip install pytest ruff
```

On Windows (Git Bash), the first two lines are `py -m venv .venv` and
`source .venv/Scripts/activate`.

**`No module named pytest` or `command not found: pytest`:** the venv isn't
active (open a new terminal? run `source .venv/bin/activate` again, or
`source .venv/Scripts/activate` on Windows), or
pytest isn't installed in it. Prefer `python -m pytest`: it always uses the
active Python.

**`python3: command not found` on Windows:** use `py` instead of `python3`.

**Tests pass locally but fail in CI:** check which Python versions CI uses.
The project may test several (`requires-python`, tox/nox sessions).

## 11. PR opened in the wrong place

If your PR's title says `YOUR-USERNAME wants to merge ... into
YOUR-USERNAME:main`, it was opened inside your fork instead of the original
project. Close it, then open it again against the original:

```bash norun
gh pr create --repo OWNER/REPO --fill
```

Or, in the browser, on the compare page set **base repository** to the
original project.

## 12. Files that shouldn't be committed

Your PR includes `.venv/`, `__pycache__/`, `.DS_Store` or similar. Remove
them from git **without deleting them from your computer**, and make sure
they're ignored:

```bash norun
git rm -r --cached .venv
echo ".venv/" >> .gitignore
git add .gitignore
git commit -m "Stop tracking .venv"
git push
```

Many projects already ignore these. If theirs doesn't, don't add your own
entries to *their* `.gitignore` in the same PR: just remove the files.

## 13. Push refused: workflow scope

```text
! [remote rejected] my-branch -> my-branch (refusing to allow an OAuth App to
create or update workflow `.github/workflows/....yml` without `workflow` scope)
```

You did nothing wrong. Since you forked, the original project changed one of
its GitHub Actions workflow files (in `.github/workflows/`). Your branch
carries that change into your fork, and the login `gh auth login` made isn't
allowed to change workflow files. `gh repo sync` stops for the same reason.

Give your login that one extra permission, then push again:

```bash norun
gh auth refresh -h github.com -s workflow
git push
```

It shows a one-time code and opens your browser, as in Lesson 03. You only
do this once.

## Clean up the sandbox

```bash
cd ..
rm -rf trouble-sandbox practice-remote.git
```

## Still stuck?

[Open an issue](https://github.com/thejesh23/first-python-contribution/issues/new)
here with **the exact command you ran and the full output**. Remove anything
you don't want public first.
