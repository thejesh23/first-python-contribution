# Lesson 12: CI and code review

**Time:** 4 minute video · 40 minute exercise
**You'll need:** Lessons 04 and 10

Opening the PR isn't the end. Almost every PR gets at least one of these:

1. a **red CI check**
2. **"This branch has conflicts that must be resolved"**
3. **review comments** asking for changes
4. a request to **squash** your commits

None of them means you did something wrong. They're the normal back-and-forth
of every PR. This lesson covers all four, and you'll practise the git parts
in a safe lab on your computer.

## 1. When CI is red

Scroll to the bottom of your PR, or run:

```bash norun
gh pr checks
gh run view --log-failed
```

(Not run in CI: they need a real PR.) `--log-failed` prints just the
failing steps' output. **Read the last 20 lines first**: that's where
pytest, ruff and friends say what went wrong.

| What failed | What it usually means | What to do |
|---|---|---|
| lint / format / pre-commit | Style issue | Run the project's formatter and linter locally (Lesson 07), commit, push |
| tests on one Python version or OS | Your code depends on something that differs there | Run that version locally with tox/nox, or read the traceback carefully |
| tests that fail on `main` too, or pass on re-run | A **flaky** or already-broken test, not you | Say so in a comment: "This failure also happens on main" |
| CLA / DCO | Legal check (Lesson 06) | Sign the CLA, or add sign-offs |
| "Waiting for approval" / "awaiting approval" | GitHub doesn't run first-time contributors' workflows until a maintainer approves | Nothing: wait. A maintainer will click approve |

**Push the fix to the same branch.** Your PR updates by itself. Never open
a new PR for the same change.

## Set up the lab

The rest of this lesson happens in a practice world on your computer: a
fake project, a fake fork and your clone, with a PR "open". Run from your
course folder:

```bash
python3 tools/conflict_lab.py ../conflict-lab
cd ../conflict-lab/work
cat ../REVIEW.md
git log --oneline
```

```text
# Review comments on your pull request

1. **CI:** This branch has conflicts that must be resolved.
2. **Reviewer:** Could you add a docstring to `greeting()`?
3. **Reviewer (later):** Looks good! Please squash into one commit before we merge.
```

You're on branch `fix-greeting`, with one commit that adds `!` to a
greeting. While your PR waited, a maintainer changed the same line on
`main`. Let's handle the three comments.

## 2. Conflicts: rebase on the latest upstream

Bring your branch up to date by **replaying your commit on top of the
latest `main`**:

```bash expect-fail
git fetch upstream
git rebase upstream/main
```

(This block stops with a conflict on purpose.) git stops and tells you
(your commit hash will be different):

```text
CONFLICT (content): Merge conflict in app.py
error: could not apply 5cf76f3... Add an exclamation mark to the greeting
```

Open `app.py`:

```text
def greeting(name):
<<<<<<< HEAD
    return f"Hello, {name}"
=======
    return "Hello " + name + "!"
>>>>>>> 5cf76f3 (Add an exclamation mark to the greeting)
```

- Between `<<<<<<<` and `=======`: what's on `main` now (the maintainer's change).
- Between `=======` and `>>>>>>>`: your commit.

**Don't just pick one side.** Keep what both changes meant: the
maintainer's f-string and comma, *and* your `!`. Edit `app.py` so it reads
exactly this, with no markers left (or run the `cat` line below to make the
same edit):

```bash
cat > app.py <<'EOF'
def greeting(name):
    return f"Hello, {name}!"
EOF
python3 -c "from app import greeting; print(greeting('Ada'))"
git add app.py
git rebase --continue
git log --oneline
```

```text
Hello, Ada!
```

`git rebase --continue` may open your editor with your commit message; save
and close it. Your commit now sits on top of the maintainer's.

In a real project, **run the tests** at this point. Then update your PR:

```bash
git push --force-with-lease
```

You rewrote your branch's history, so a plain `git push` is refused.
`--force-with-lease` replaces it, but only if nobody else pushed to your
branch since you last fetched. **Never use plain `--force`.**

> **Rebase or merge?** GitHub's **Update branch** button *merges* `main`
> into your branch instead. Some projects are fine with that; many prefer
> rebasing. CONTRIBUTING usually says. If it doesn't, rebase.

If a rebase goes wrong, `git rebase --abort` puts everything back the way it
was before you started.

## 3. Review comments

Reviewers leave three kinds of feedback:

- **A comment or question.** Reply to it, briefly, in your own words.
- **A suggestion** (a code block with a **Commit suggestion** button). Click
  it to apply the change directly, or use **Add suggestion to batch** for
  several at once.
- **"Changes requested".** Fix what's asked, push, then click the 🔄
  **Re-request review** button next to the reviewer's name.

Back in the lab, the reviewer asked for a docstring. Make the change as a
**new commit** and push normally:

```bash
cat > app.py <<'EOF'
def greeting(name):
    """Return a friendly greeting for name."""
    return f"Hello, {name}!"
EOF
git commit -am "Add a docstring to greeting"
git push
```

Then reply on the review comment with one short line, for example:
"Added in 3f2a1b9." Naming the commit lets the reviewer check it in one click.

**See an example** (made for this course): [a review with changes requested](https://github.com/thejesh23/graduation-test-project/pull/3/files): an inline comment, the fix as a new commit, a one-line reply naming it, then approval and merge.

**Review etiquette:**

- **New commits while review is going on.** They let reviewers see exactly
  what changed since they last looked. Don't force-push mid-review unless
  asked (rebasing for a conflict is fine).
- **Don't resolve the reviewer's conversations yourself** unless the
  project says to. Let them mark it resolved once they're happy.
- **Disagreeing is fine.** Explain your reasoning once, politely, then go
  with the maintainer's decision. It's their project.
- **Don't know how to do what they asked?** Say so and ask. That's normal.

## 4. Squash when asked

Some projects want one tidy commit per PR. When the reviewer asks you to
squash, combine your commits into one:

```bash
git reset --soft upstream/main
git commit -m "Add an exclamation mark to the greeting"
git log --oneline
git push --force-with-lease
```

`git reset --soft upstream/main` un-does your commits but **keeps all your
changes staged**, so the next commit contains everything. Write a commit
message that describes the whole change (Lesson 10).

The other common way, which lets you choose commit by commit, is an
interactive rebase:

```bash norun
git rebase -i upstream/main
```

Your editor opens with a list of your commits. Leave the first as `pick`,
change the others to `squash` (or `s`), save and close. Then edit the
combined message.

Many projects squash for you when they merge (**Squash and merge**). Only do
it yourself when asked.

## Clean up the lab

```bash
cd ../..
rm -rf conflict-lab
```

Next: [Lesson 13: using AI tools well](../13-using-ai-well/).
