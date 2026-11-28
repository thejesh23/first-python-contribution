# Lesson 11: Opening the pull request

**Time:** 3 minute video · 20 minute exercise
**You'll need:** your `fix-slugify` branch from Lesson 10

Your change is ready. Now you hand it to a reviewer, who has many other
pull requests waiting. The **title** and **description** decide how fast
yours gets looked at, and how many questions come back.

## Before you open it

- **One change per PR.** A fix and a refactor are two PRs. Small PRs get
  reviewed first.
- **Read your own diff once**, as if you were the reviewer. Remove stray
  `print` calls, commented-out code and formatting changes to lines you
  didn't mean to touch.
- **Run what CI runs**: the tests and the linters (Lesson 10, Step 4).

## The title

The title is what maintainers see in a list of a hundred PRs. Say what the
PR **does**, the way you write a commit subject:

| Weak | Why | Better |
|---|---|---|
| `Fix bug` | Which bug? | `Fix slugify for repeated spaces and punctuation` |
| `Update textkit.py` | Names a file, not a change | `Strip hyphens from the ends of slugs` |
| `Fixed the issue with slugs.` | Past tense, full stop, vague | `Collapse repeated separators in slugify` |

- Imperative mood ("Fix", not "Fixed"), 72 characters or fewer, no full stop.
- Some projects want a format. CPython puts the issue first:
  `gh-12345: Fix ...`. Others use Conventional Commits: `fix: ...`.
  CONTRIBUTING says which (Lesson 06).
- When a project squash-merges your PR, the title often becomes the commit
  message in its history. It's worth a minute.

## The description: four things

1. **The issue it fixes.** `Fixes #1234` links the issue, and closes it when
   the PR is merged. If your PR is only part of the fix, write `Refs #1234`
   instead.
2. **What changed, and why**, in two or three sentences. The diff shows
   *how*. It can't show why you chose this fix.
3. **How you tested it.** The tests you added and the commands you ran. For
   a visual change, add a before and after screenshot.
4. **Anything the reviewer should know.** A choice you weren't sure about,
   something you left out on purpose, or your AI disclosure if the project
   asks for one (Lesson 06).

```text
Fix slugify for repeated spaces and punctuation

Fixes #1234

`slugify` kept punctuation and produced doubled hyphens for repeated
spaces. It now turns every run of non-alphanumeric characters into a
single hyphen and strips hyphens from the ends.

Tested: added a parametrized regression test with the cases from the
issue; the full test suite and ruff pass locally.
```

That's the whole thing: under 60 words. **Short is good.** Long
descriptions with headings and bullet lists, for a three-line change, are
what maintainers have learned to skip (Lesson 13 shows why).

**See an example** (made for this course): [a pull request to another project](https://github.com/thejesh23/graduation-test-project/pull/3) with this shape: `Fixes #2`, what and why, and how it was tested. Merging it closed the issue.

### When the project has a template

Many projects keep a `pull_request_template.md` (in the repo root, `docs/`
or `.github/`). GitHub puts it in the description box for you. Fill in
**every** section, tick only the checkboxes that are true, and delete the
instruction comments. An untouched template tells the reviewer you didn't
read it.

## Draft pull requests

Not finished, but you want CI to run or an early opinion? Open a **draft**:
click the arrow next to **Create pull request** and choose the draft
option, or use `--draft` below. A
draft can't be merged, and reviewers aren't asked to look yet. When it's
ready, click **Ready for review**, or run `gh pr ready`.

## Opening it

Write the description in a file, so you can read it over before anyone
else does. The title goes on the command line, so the file holds only the
description, without a title line:

```bash norun
gh pr create --title "Fix slugify for repeated spaces and punctuation" --body-file description.md
gh pr create --draft --title "..." --body-file description.md   # not ready yet
```

Or in the browser: open your fork and click **Compare & pull request**, as
in Lesson 02. Two things to check before you click:

- **The arrow** at the top points from your branch to the project's `main`.
- **Allow edits from maintainers** stays ticked. It lets a maintainer push
  a small fix to your branch instead of asking you for it.

Then leave the description alone unless something changes. If you push a
fix that changes what the PR does, update the description to match.

## Practise: describe your slugify fix

Exercise 3 is local only, so you won't open this PR. But you can write it.
Put the title on the first line of a file, a blank line, then the
description, and check it:

```bash norun
python tools/check_pr_description.py pr-description.md
```

```text
✔ Title says what the PR does: "Fix slugify for repeated spaces and punctuation"
✔ Issue is linked, and will close when the PR is merged.
✔ What and why are explained.
✔ Testing is described.

Ready to open. Nice description!
```

Next: [Lesson 12: CI and code review](../12-ci-and-review/).
