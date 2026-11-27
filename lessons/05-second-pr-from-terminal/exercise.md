# Exercise 05: A function, a test, a green CI

- [ ] `git fetch upstream`
- [ ] Create and activate `.venv`, then `python -m pip install pytest ruff`
- [ ] `git switch -c exercise-2 upstream/main`
- [ ] Write `practice/tests/test_YOUR_NAME.py` and watch it fail
- [ ] Write `practice/greetings/YOUR_NAME.py` and watch it pass
- [ ] `ruff format practice` and `ruff check practice` are clean
- [ ] Commit only your two files, then `git push -u origin exercise-2`
- [ ] `gh pr create --fill` (after `gh repo set-default thejesh23/first-python-contribution`)
- [ ] `gh pr checks --watch` until the check is green, then wait for the bot's comment and the merge
      (no checks yet? Your first run waits for a maintainer's approval until your Lesson 02 PR is merged.
      After that merge, push one more commit and the check starts by itself)
- [ ] Tidy up: `git switch main`, `git pull upstream main`, `git branch -d exercise-2`

**Stretch 1:** add a second test, for example that `greet("")` still returns
a string. Run it, commit, push, and watch your PR update.

**Stretch 2:** before the merge, open your PR on GitHub, go to **Checks →
Exercise 2 tests**, and find the line where pytest ran your test.
