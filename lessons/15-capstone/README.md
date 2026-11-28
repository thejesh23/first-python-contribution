# Lesson 15: Capstone: your first external contribution

**Time:** 3 minute video · 1–4 weeks, mostly waiting for review
**You'll need:** everything so far

Time to do it for real: a **merged pull request in an open source project
you don't own**. When it's merged, you add yourself to the
[graduates wall](../../graduates/), and a bot checks your PR on GitHub before
letting you in.

## What counts

- A **merged** PR (not just opened) on **GitHub**
- In a project you **don't own**, that **isn't a fork**, and isn't this
  course or a practice repo
- **Opened by you, merged by a maintainer** (not by you)
- Code, tests **or docs**: all count

What doesn't count, even if it gets merged: whitespace-only changes, spelling
"fixes" that aren't errors, or anything opened just to tick a box.
Maintainers can tell, and it costs them time. The test: **would the
maintainer have wanted this change even if you weren't doing a course?**

## The capstone, stage by stage

Copy this checklist into your notes. Each stage links to the lesson that
covers it.

### 1. Choose (Lesson 08)

- [ ] Shortlist 2–3 issues with `tools/find_issues.py`, GitHub search, or a
      project you use
- [ ] Do the five checks on each: thread read, unassigned, no PR, agreed, reproduced
- [ ] Prefer small: a docs fix or a small bug is a great capstone

### 2. Read the house rules (Lesson 06)

- [ ] CONTRIBUTING (or developer guide) read in full
- [ ] CLA signed or DCO sign-off ready, if needed
- [ ] AI policy noted, with its disclosure format
- [ ] Claimed the issue, if the project wants that, and got a go-ahead

### 3. Set up (Lesson 07)

- [ ] Forked and cloned: `gh repo fork OWNER/REPO --clone`
- [ ] Set up the way CONTRIBUTING says (`tools/which_setup.py` helps)
- [ ] The tests pass **before** you change anything

### 4. Make the change (Lesson 10)

- [ ] On a branch, never `main`
- [ ] Reproduced, with a failing test where it makes sense
- [ ] Smallest fix; docs and changelog updated if the project wants them
- [ ] Tests and linters pass locally
- [ ] Clear commit message (with sign-off or trailer if required)

### 5. Open the PR (Lesson 11)

- [ ] Pushed to your fork; PR opened against the project's main branch
- [ ] A title that says what the PR does
- [ ] Template filled in; `Fixes #...`; what changed and why; how you tested it
- [ ] Written in your own words; AI use disclosed if the project asks (Lesson 13)

### 6. Review (Lesson 12)

- [ ] CI green (or failures explained)
- [ ] Every review comment answered; new commits pushed; review re-requested
- [ ] Conflicts resolved with a rebase if needed

### 7. Wait, then graduate (Lesson 14)

- [ ] One polite nudge after ~2 weeks of silence, at most
- [ ] **Merged!**

While you wait for review, it's fine to start on a second candidate in
another project. Just don't claim more than you can actively work on.

## Graduate

Once your PR is merged, in **this course repo**:

1. Sync your fork's `main` (`git switch main`, `git pull upstream main`) and
   make a branch: `git switch -c graduate`.
2. Create `graduates/YOUR-USERNAME.py`:

   ```python
   name = "Ada Lovelace"
   github = "ada"
   pr = "https://github.com/OWNER/REPO/pull/123"
   message = "One sentence: what you changed, or what you learned"
   ```

3. Commit, push, and open a pull request, like Lesson 05. If the push is
   refused with `without workflow scope`, the course changed a workflow file
   since you forked:
   [Troubleshooting, section 13](../A-troubleshooting/#13-push-refused-workflow-scope)
   has the one-command fix.

The **Validate graduate** bot looks up your PR on GitHub and checks it's
merged, yours, merged by someone else, and in a real project you don't own.
If everything checks out, it comments 🎓, and once a maintainer merges it you
appear on the [graduates wall](../../graduates/). If not, its comment says exactly what's
wrong.

**See an example** (made for this course): [a graduate pull request](https://github.com/thejesh23/first-python-contribution/pull/73), linking [a merged contribution to another project](https://github.com/thejesh23/graduation-test-project/pull/3).

Contributed somewhere other than GitHub (GitLab, Codeberg, a mailing list)?
Congratulations, that counts too. The bot can only check GitHub, so
[open an issue](https://github.com/thejesh23/first-python-contribution/issues/new)
with a link and we'll add you by hand.

## What now?

You can contribute to any open source project now. A few ideas:

- **Go back to the same project.** Your second PR there will be much easier,
  and maintainers remember helpful people.
- **Help the next beginner.** Answer a question in this course's issues,
  review someone's first-commit PR, or improve a lesson that confused you.
- **Bookmark the [troubleshooting page](../A-troubleshooting/)** for when
  something odd happens.

### Now you can use AI agents

You did this whole course by hand, so you know the basics. For your next
contributions, go ahead and use agentic tools like Claude Code, Codex or
Cursor. They speed up the work, and now you can check what they did.

Be careful about one thing: **read the project's AI policy first.** Some
projects, including well-known ones, don't accept AI-assisted pull requests
at all (Lesson 06 names Gentoo, NetBSD and QEMU). Others accept them only if
you disclose it. And everywhere, you still answer for every line and write
your own comments (Lesson 13).

Welcome to open source. 🎓
