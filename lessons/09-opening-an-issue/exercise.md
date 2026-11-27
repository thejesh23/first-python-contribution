# Exercise 09: The bug hunt

`bug-hunt/splitbill.py` has **five** bugs on purpose. Find one and report it
the way a maintainer would want.

- [ ] In the course folder, check the bug hunt is there: `ls bug-hunt`. (Missing? Your fork is older than this
      lesson: `git fetch upstream`, then `git switch -c bug-hunt upstream/main`.)
- [ ] Read [`bug-hunt/README.md`](../../bug-hunt/README.md): it's the spec, what splitbill *should* do
- [ ] Try splitbill with different bills, people, tips and tax, and compare with the README
- [ ] Found something different? Make it **minimal**: the smallest numbers and fewest options that still show it
- [ ] Note your versions:

  ```bash
  python bug-hunt/splitbill.py --version
  python --version
  ```

- [ ] Search the [issues](https://github.com/thejesh23/first-python-contribution/issues) for your bug. Here a
      duplicate is fine, since other learners hunt the same bugs; in a real project, add to the existing issue instead
- [ ] Open **Issues → New issue → Bug hunt: report a splitbill bug**, fill in every field, and submit.
      Use the form in the browser, not `gh issue create`: the form adds the `bug-hunt` label the bot looks for,
      and only maintainers can add labels from the command line
- [ ] Read the bot's comment. Fix any ✘ by editing your issue (**···** → **Edit**); the bot checks again when you save
- [ ] A maintainer reviews your report and then closes it. Closed here means reviewed, not rejected: the bug stays

Please **don't** open a pull request that fixes the bug: the next learner
needs it.

**Stretch:** find all five, and report each one as its own issue. One bug
per issue.

<details><summary>Stuck? Hints (try for 10 minutes first)</summary>

- Split a bill that doesn't divide evenly.
- Write the tip the way the README says you may.
- What about nobody at all?
- Add tax *and* a tip, and work the tip out by hand.
- Try a big bill.
</details>
