# Lesson 09: Opening a good issue

**Time:** 3 minute video · 30 minute exercise
**You'll need:** this repo cloned (Lesson 05)

Sometimes there's no issue to pick up: you found a bug yourself, or a docs
page that's wrong, or you want a feature. Then **you** open the issue. A
good one gets fixed, sometimes by you. A vague one gets a "can't reproduce"
and is closed.

## Many projects want the issue first

Before a pull request, many projects want an issue, so maintainers can agree
on **what** to change before anyone spends time on **how**. Two examples
from big Python projects:

- **CPython:** a PR fixes an existing issue and puts its number in the PR
  title, like `gh-12345: Fix ...`. Found something new? Open an issue first.
  Only trivial changes, like typo fixes in the docs, can skip it.
- **Django:** "All contributions require a ticket unless the change is
  considered trivial." Django tracks tickets in its own tracker, Trac, not
  GitHub issues. Typo fixes and small wording changes count as trivial.

Other projects say "open an issue to discuss before large changes", and
some close PRs that don't link one. **CONTRIBUTING says which** (Lesson 06).
When it doesn't, an issue first is never wrong for anything beyond a typo.

## Before you open one

1. **Search first, open *and* closed issues.** Use a few words from the
   error message. If someone already reported it, add what's new to that
   issue (your versions, a smaller example), or a 👍 reaction. Don't post
   "+1" or "same here": it notifies everyone and adds nothing.
2. **Try the latest version.** It may already be fixed. Say in the report
   which version you tried.
3. **Questions aren't issues.** "How do I...?" goes to the project's forum,
   chat or GitHub Discussions, if it has them. CONTRIBUTING or the README
   will say where.
4. **Security bugs are never public issues.** If the bug lets someone do
   harm (read secrets, run code, crash a server), read the project's
   `SECURITY.md`, or use **Report a vulnerability** on the repo's security
   tab if the project has turned it on. A public issue tells attackers before
   there's a fix.

## What a good bug report contains

| Part | What to write |
|---|---|
| **Title** | What goes wrong, and when. `splitbill: shares don't add up for 3 people`, not `Bug` or `Help!!` |
| **What went wrong** | One or two sentences, in your own words |
| **Steps to reproduce** | The exact command or code someone can paste and run |
| **Expected** | What should happen, and why: quote the docs if they say so |
| **Actual** | What happens instead: the output pasted as **text**, the **whole** traceback, never a screenshot of text |
| **Versions** | The package (`python -m pip show NAME`), Python (`python --version`), your operating system |

One bug per issue. If you found two, open two issues: they may be fixed at
different times, by different people.

Most projects have an **issue template** or **form** that asks for exactly
these. When you click **New issue**, pick the matching one (Bug report,
Feature request...) and fill in every field.

## The minimal example

The steps to reproduce matter most. A maintainer has to see the bug before
they can fix it, and they won't set up your whole app to do that.

Make the example **minimal**: remove everything that isn't needed to show
the bug, and check after each cut that the bug is still there. Smaller
numbers, fewer options, no code from your own project. Often you'll find
the cause while you cut, and that's a great thing to add to the report.

```text
Steps to reproduce:
    python bug-hunt/splitbill.py 10 --people 3

Expected: shares of $3.34, $3.33 and $3.33, which add up to $10.00.
README.md says "the shares always add up to the total, to the cent".

Actual:
    Person 1: $3.33
    Person 2: $3.33
    Person 3: $3.33
```

## Feature requests

Start with the **problem**, not the solution: "I split bills with tips in
other currencies, and splitbill always shows `$`" lets maintainers find the
best fix. A proposal is welcome after that, but they may want something
else. Wait for a yes before you write the code.

## After you open it

- **Answer questions quickly.** "Which version?" unanswered for a month
  usually means the issue gets closed.
- **Want to fix it yourself?** Say so in the issue, then follow Lesson 08's
  claiming advice.
- **Link your PR.** `Fixes #123` in the PR description closes the issue
  when the PR is merged into the default branch. `Closes` and `Resolves`
  work too.
- **Write it yourself.** Like comments and PRs, an issue is in your own
  words, with output you really saw (Lessons 06 and 13).

## The bug hunt

This repo includes a small program with bugs on purpose:
[`bug-hunt/splitbill.py`](../../bug-hunt/), which splits a restaurant bill
between friends. Its [README](../../bug-hunt/README.md) says how it
*should* behave. Try it and compare:

```bash
python bug-hunt/splitbill.py 120 --people 4 --tip 15
```

```text
Bill:  $120.00
Tax:   $0.00
Tip:   $18.00 (15%)
Total: $138.00

Person 1: $34.50
Person 2: $34.50
Person 3: $34.50
Person 4: $34.50
```

That one's right. Others aren't. Find a bug, then report it with the
**Bug hunt** issue form (the exercise has the steps). A bot checks your
report within a minute: it runs your command and compares the result
with a correct splitbill, so it knows if your steps really show the bug.
Then a maintainer reviews it, and closes it. The bug has to stay for the
next learner, so here a closed report means **reviewed**, not rejected. (In
a real project, a good report stays open until the bug is fixed.)

**See an example** (made for this course): [a bug-hunt report](https://github.com/thejesh23/first-python-contribution/issues/72) made with the form, the bot's check, and the maintainer's review.

Next: [Lesson 10: making the change](../10-making-the-change/).
