# Lesson 08: Finding an issue (that nobody else is working on)

**Time:** 3 minute video · 30 minute exercise
**You'll need:** `gh` logged in (Lesson 03)

The most common way beginners waste a weekend: they pick an issue, work on
it for days, open a PR, and find someone else fixed it last week. This
lesson is about picking well.

## Be realistic about "good first issue"

Popular projects label easy issues `good first issue`, and those get taken
fast, often within days. When we checked in November 2026, pytest had just
one open `good first issue`, and someone was already assigned to it.

So widen your net:

- **Other labels:** `help wanted`, `easy`, `beginner`, `documentation`,
  `first-timers-only`. Every project names them differently; check its
  **Labels** page.
- **Projects you actually use.** You understand them, and you'll notice
  their rough edges.
- **Problems you hit yourself.** A confusing error, a broken docs example,
  a setup step that failed in Lesson 07: those are real contributions, and
  nobody else is working on them.

## Searching on GitHub

GitHub's issue search understands filters. Paste this into the search box
at <https://github.com/search> (choose **Issues**):

```text
is:issue is:open label:"good first issue" no:assignee -linked:pr language:python
```

| Filter | Means |
|---|---|
| `is:open` | Not closed |
| `label:"good first issue"` | Has that label |
| `no:assignee` | Nobody is assigned |
| `-linked:pr` | No pull request is linked to it yet |
| `language:python` | In a mostly-Python repository |
| `repo:pallets/flask` | Only in that repository |

## The course's issue finder

That search returns a lot of tiny personal projects. `tools/find_issues.py`
does better. It first finds active Python projects with 500+ stars and open
good-first issues, then searches those projects using the filters above. It
drops issues an open PR already mentions, and flags issues where someone has
commented "I'd like to work on this":

```bash norun
python3 tools/find_issues.py
python3 tools/find_issues.py --label "help wanted"
python3 tools/find_issues.py --repo pallets/flask --label "docs"
```

```text
pipeshub-ai/pipeshub-ai (★4140)  Re-enable Greenhouse in the MCP server catalog
    https://github.com/pipeshub-ai/pipeshub-ai/issues/5044
    opened 23 days ago, 0 comments

26 of 62 issues look free. Read each thread fully before you claim one.
```

Your list will be different: issues are claimed and closed every day. These
are **candidates**, not guarantees. The next part is the real check.

## Before you claim: the five checks

For each candidate, open it and check:

1. **Read the whole thread**, every comment. The answer is often in comment
   14: "we decided not to do this" or "fixed in 2.3".
2. **Is someone already on it?** Look at **Assignees** and at the comments.
   A claim from months ago with no PR may be abandoned; see below.
3. **Is there a PR already?** Look at **Development** in the sidebar, then
   search the project's PRs, including closed ones:

   ```bash norun
   gh pr list --repo pallets/flask --state all --search "1234"
   ```

   A closed, unmerged PR is worth reading: it shows what the maintainers
   didn't want.
4. **Is it agreed?** Labels like `needs triage`, `needs decision` or
   `question` mean the maintainers haven't decided what they want yet. Don't
   start coding.
5. **Is it still a problem?** Try to reproduce it on the latest `main`
   (your Lesson 07 setup). Bugs get fixed without anyone closing the issue.

## Claiming it

Check CONTRIBUTING first (Lesson 06). Some projects say "don't ask, just
open a PR"; others assign issues. If it's not stated, comment in your own
words, briefly, with your plan:

```text
Hi! I'd like to work on this. I can reproduce it on main: `parse("")`
raises IndexError. My plan is to return an empty list and add a test.
Does that sound right?
```

That shows you read the issue, checked it still happens, and have a plan,
so a maintainer can answer in one line. **See an example** (made for this course): [a claim and the maintainer's one-line answer](https://github.com/thejesh23/graduation-test-project/issues/2). Then **wait** for a reply if the
project assigns issues. Silence for a few days is normal.

**Don't:**

- claim several issues at once, or claim one you can't start this week
- write "can I work on this?" with nothing else
- use an AI tool to write the comment (Lesson 06)

## When someone else claimed it first

If a claim is weeks old with no PR and no updates, ask kindly:

```text
Hi @someone, are you still working on this? If not, I'd be happy to
pick it up.
```

Give it a week. If there's no answer, ask a maintainer whether you can
take over. If you do, mention the earlier person in your PR. They may have
useful notes.

## Your claim is accepted. Now what?

Fork the project (Lesson 02's **Fork** button, or
`gh repo fork OWNER/REPO --clone`), set it up (Lesson 07), make a branch,
and start. Lesson 10 is about making the change itself.

No issue for what you want to fix yet? Then you write it, and many
projects want that before any pull request. That's the next lesson.

Next: [Lesson 09: opening a good issue](../09-opening-an-issue/).
