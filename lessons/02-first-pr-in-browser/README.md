# Lesson 02: Star, fork, and your first commit, in the browser

**Time:** 3 minute video · 10 minute exercise
**You'll need:** a GitHub account. Nothing to install.

By the end of this lesson you'll have a merged pull request in a public
repository: this one.

## Three words you'll use forever

| Word | What it means |
|---|---|
| **Star** ⭐ | A bookmark. Starring a repo saves it to your list of stars and tells others it's useful. It changes nothing in the code. |
| **Fork** | Your own copy of someone else's repo, under your account. You can change your fork freely; the original is untouched. |
| **Commit** | A saved snapshot of a change, with a message saying what changed. |
| **Pull request** | A request to the original repo: "please pull my commit in." |

## Step 1: Star the repo

Open <https://github.com/thejesh23/first-python-contribution> and click
**Star** near the top right. Starring is optional. It bookmarks the course
so you can find it again, and it helps other beginners find it.

## Step 2: Fork the repo

Click **Fork** (next to Star), then **Create fork**. After a few seconds
you're looking at `github.com/YOUR-USERNAME/first-python-contribution`.
Check the top left: it says **forked from thejesh23/first-python-contribution**.
That's your copy.

## Step 3: Make your first commit

In **your fork**:

1. Open the `first-commits` folder.
2. Click **Add file → Create new file**.
3. Name the file **your GitHub username** followed by `.py`, for example
   `octocat.py`. It must match your username exactly.
4. Paste this and fill it in:

   ```python
   name = "Your Name"
   github = "your-github-username"
   message = "Why you're learning Python"
   ```

5. Click **Commit changes...**. Write a commit message such as
   `Add first commit for octocat`, keep **Commit directly to the main
   branch** selected (this is your fork, so that's fine), and click
   **Commit changes**.

You just made a commit. It's in your fork, not the original repo yet.

> **Why a Python file?** It's three lines of real Python: three variables
> holding strings. The bot checks it with Python's own parser, the same way
> Python reads your code before running it.

## Step 4: Open a pull request

1. Go to the main page of your fork. You'll see a banner: **This branch is
   1 commit ahead of thejesh23/first-python-contribution:main**.
2. Click **Contribute → Open pull request**.
3. Check the arrow at the top: **base repository: thejesh23/first-python-contribution**
   ← **head repository: YOUR-USERNAME/first-python-contribution**.
4. Keep the title, add a sentence to the description if you like, and click
   **Create pull request**.

## Step 5: Watch the bot

Within a minute or two:

- A check called **Validate first commit** runs. Scroll down on your PR to
  see it.
- If your file is right, the bot comments 🎉 and **merges your PR**, usually
  within a minute. The purple **Merged** badge means your commit is now part
  of the project.
- If something's wrong, the bot comments with exactly what to fix. Fix it in
  your fork (open your file, click the ✏️ pencil, commit). Your PR updates
  automatically and the check runs again.

**See an example** (made for this course): [a first pull request](https://github.com/thejesh23/first-python-contribution/pull/70), opened from the fork's **Contribute** button, checked and merged by the bot 15 seconds later.

## What you just did

That's the same workflow behind every open source contribution: **fork →
commit → pull request → automated checks → merge**. In real projects a human
reviews it and merges it, and the checks run tests instead of reading three
lines. Here a bot merges your first commit, so you don't have to wait. You
meet a human reviewer in your next pull request, in Lesson 05.

## Common problems

| Bot says | Fix |
|---|---|
| File name doesn't match your username | Rename the file to exactly `YOUR-USERNAME.py`, same capitals as your profile. |
| Changes files outside `first-commits/` | You edited another file too. Undo that change in your fork. |
| Isn't valid Python | Usually a missing quote. Each value needs `"` at both ends. |
| `github` doesn't match | The `github = "..."` value must be your username. |
| Can't contain links or @mentions | Nobody reads your file before the bot merges it, so `name` and `message` must be plain words. |

Next: [Lesson 03: set up your machine](../03-set-up-your-machine/).
