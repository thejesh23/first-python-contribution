import re
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import check_graduate as g  # noqa: E402
import graduates_wall as wall  # noqa: E402

GOOD = (
    'name = "Ada Lovelace"\n'
    'github = "ada"\n'
    'pr = "https://github.com/psf/requests/pull/123"\n'
    'message = "Fixed a docs example."\n'
)


def pr_data(**overrides):
    data = {
        "merged": True,
        "user": {"login": "ada"},
        "merged_by": {"login": "maintainer"},
        "base": {"repo": {"full_name": "psf/requests", "owner": {"login": "psf"}, "fork": False}},
    }
    data.update(overrides)
    return data


def test_good_file_and_pr():
    result, values = g.parse_source(GOOD)
    assert result.ok and values["pr"].endswith("/pull/123")
    assert g.check_values(values, "ada").ok
    assert g.check_pr_data(pr_data(), "ada").ok


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (GOOD.replace('message = "Fixed a docs example."\n', ""), "`message` is missing"),
        (GOOD + "import os\n", "use only four lines"),
        (GOOD.replace("Ada Lovelace", ""), "`name` is empty"),
        ('name = "x\n', "isn't valid Python"),
    ],
)
def test_bad_sources(source, expected):
    result, _ = g.parse_source(source)
    assert any(expected in e for e in result.errors), result.errors


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ({"github": "bob", "pr": "https://github.com/a/b/pull/1"}, "opened by `ada`"),
        ({"github": "ada", "pr": "https://gitlab.com/a/b/-/merge_requests/1"}, "GitHub pull request link"),
        ({"github": "ada", "pr": "https://github.com/a/b/issues/1"}, "GitHub pull request link"),
    ],
)
def test_bad_values(values, expected):
    assert any(expected in e for e in g.check_values(values, "ada").errors)


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (pr_data(merged=False), "isn't merged yet"),
        (pr_data(user={"login": "bob"}), "opened by `bob`"),
        (pr_data(merged_by={"login": "ada"}), "merged that pull request yourself"),
        (
            pr_data(base={"repo": {"full_name": "ada/tool", "owner": {"login": "ada"}, "fork": False}}),
            "your own repository",
        ),
        (pr_data(base={"repo": {"full_name": "bob/requests", "owner": {"login": "bob"}, "fork": True}}), "is a fork"),
        (
            pr_data(
                base={
                    "repo": {
                        "full_name": "firstcontributions/first-contributions",
                        "owner": {"login": "firstcontributions"},
                        "fork": False,
                    }
                }
            ),
            "practice repository",
        ),
    ],
)
def test_bad_prs(data, expected):
    assert any(expected in e for e in g.check_pr_data(data, "ada").errors)


def test_merged_by_missing_is_accepted():
    assert g.check_pr_data(pr_data(merged_by=None), "ada").ok


@pytest.mark.parametrize(
    ("paths", "expected"),
    [(["graduates/ada.py"], True), (["graduates/README.md"], False), (["first-commits/ada.py"], False)],
)
def test_is_learner_pr(paths, expected):
    assert g.is_learner_pr(paths) is expected


def test_validate_with_fake_github(tmp_path, monkeypatch):
    def git(*args):
        return subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True, text=True).stdout.strip()

    git("init", "-q", "-b", "main")
    git("config", "user.email", "t@example.com")
    git("config", "user.name", "t")
    (tmp_path / "graduates").mkdir()
    (tmp_path / "graduates/README.md").write_text("wall\n")
    git("add", ".")
    git("commit", "-qm", "base")
    base = git("rev-parse", "HEAD")
    (tmp_path / "graduates/ada.py").write_text(GOOD)
    git("add", ".")
    git("commit", "-qm", "graduate")
    monkeypatch.chdir(tmp_path)
    assert g.validate("ada", base, "HEAD", fetch=lambda url: pr_data()).ok
    assert not g.validate("ada", base, "HEAD", fetch=lambda url: None).ok
    assert not g.validate("ada", base, "HEAD", fetch=lambda url: pr_data(merged=False)).ok


def test_wall_escapes_and_lists(tmp_path):
    (tmp_path / "ada.py").write_text(GOOD.replace("Fixed a docs example.", "<img src=x> [click](https://evil) | *hi*"))
    (tmp_path / "broken.py").write_text("name = 'x")
    text = wall.render(tmp_path)
    assert "**1 graduate**" in text
    assert "[psf/requests#123](https://github.com/psf/requests/pull/123)" in text
    assert "\\<img src=x\\>" in text, "the message's own <img> must be escaped"
    images = re.findall(r"(?<!\\)<img [^>]*>", text)
    assert len(images) == 1 and 'src="https://github.com/ada.png?size=128"' in images[0], "only the profile picture"
    assert "](https://evil)" not in text
    assert "\\|" in text


def test_wall_empty(tmp_path):
    assert "No graduates yet" in wall.render(tmp_path)


def test_photos_link_to_profiles_and_escape_names(tmp_path):
    risky = "name = 'Ada \"><script>x</script>'\n"
    (tmp_path / "ada.py").write_text(risky + GOOD.split("\n", 1)[1])
    text = wall.render(tmp_path)
    assert '<a href="https://github.com/ada"><img src="https://github.com/ada.png?size=128"' in text
    assert 'alt="@ada"' in text and 'width="64" height="64"' in text
    assert "<script>" not in text and "&lt;script&gt;" in text
    assert 'title="Ada &quot;&gt;' in text, "the name can't break out of the title"


def test_front_page_strip_shows_the_newest_and_links_to_the_wall(tmp_path, monkeypatch):
    for n in range(wall.STRIP_MAX + 5):
        (tmp_path / f"user{n:02}.py").write_text(GOOD.replace('"ada"', f'"user{n:02}"'))
    monkeypatch.setattr(wall, "added_time", lambda path: int(path.stem[4:]))  # user34 is the newest
    block = wall.strip(tmp_path)
    assert f"**{wall.STRIP_MAX + 5} graduates**" in block and "[See the wall](graduates/)" in block
    assert f"Here are the {wall.STRIP_MAX} most recent, newest first." in block
    assert block.count("<img ") == wall.STRIP_MAX
    assert "user34.png" in block and "user05.png" in block and "user04.png" not in block
    assert block.index("user34.png") < block.index("user33.png"), "newest first"
    assert 'width="48" height="48"' in block
    assert "You could be the first" in wall.strip(tmp_path / "nobody")


def test_front_page_is_only_changed_between_the_markers():
    page = f"# Title\n\ntext\n\n{wall.START}\nold\n{wall.END}\n\n## License\n"
    updated = wall.update_front_page(page, "new\n")
    assert updated == f"# Title\n\ntext\n\n{wall.START}\nnew\n{wall.END}\n\n## License\n"
    assert wall.update_front_page(updated, "new\n") == updated, "running it twice changes nothing"
    assert wall.update_front_page("no markers here", "new\n") == "no markers here"


def test_the_repo_front_page_has_the_markers():
    text = (wall.ROOT / "README.md").read_text(encoding="utf-8")
    assert text.count(wall.START) == 1 and text.count(wall.END) == 1
    assert text.index(wall.START) < text.index(wall.END)


def test_newest_means_merged_last_not_written_last(tmp_path, monkeypatch):
    """A learner can write their file days before it's merged; the strip orders by the merge."""

    def git(*args, when=None):
        env = None
        if when:
            import os

            env = {**os.environ, "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when}
        return subprocess.run(
            ["git", *args], cwd=tmp_path, check=True, capture_output=True, text=True, env=env
        ).stdout.strip()

    git("init", "-q", "-b", "main")
    git("config", "user.email", "t@example.com")
    git("config", "user.name", "t")
    git("commit", "-q", "--allow-empty", "-m", "base", when="2026-01-01T00:00:00")
    for login, written, merged in (("early", "2026-01-02T00:00:00", "2026-01-10T00:00:00"),
                                   ("late", "2026-01-05T00:00:00", "2026-01-06T00:00:00")):  # fmt: skip
        git("switch", "-q", "-c", login, "main")
        (tmp_path / f"{login}.py").write_text(GOOD.replace('"ada"', f'"{login}"'))
        git("add", ".")
        git("commit", "-qm", login, when=written)
        git("switch", "-q", "main")
        git("merge", "-q", "--no-ff", login, "-m", f"merge {login}", when=merged)

    assert wall.added_time(tmp_path / "early.py") > wall.added_time(tmp_path / "late.py")
    block = wall.strip(tmp_path)
    assert block.index("early.png") < block.index("late.png"), "merged last, shown first"


def test_the_wall_shows_the_newest_first_and_says_so(tmp_path, monkeypatch):
    for login in ("anna", "zed"):
        (tmp_path / f"{login}.py").write_text(GOOD.replace('"ada"', f'"{login}"'))
    monkeypatch.setattr(wall, "added_time", lambda path: {"anna": 1, "zed": 2}[path.stem])  # zed is the newest
    page = wall.render(tmp_path)
    assert "**2 graduates**, the most recent first." in page
    assert page.index("zed.png") < page.index("anna.png"), "photos: newest first"
    assert page.index("[@zed]") < page.index("[@anna]"), "table: newest first"
    assert "The most recent is first." in wall.strip(tmp_path)


def test_a_graduate_added_again_counts_from_the_latest_addition(tmp_path):
    """Seen with #63, #67 and #68: added, removed, added again. The newest addition is what counts."""

    def git(*args, when=None):
        import os

        env = {**os.environ, "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when} if when else None
        return subprocess.run(
            ["git", *args], cwd=tmp_path, check=True, capture_output=True, text=True, env=env
        ).stdout.strip()

    git("init", "-q", "-b", "main")
    git("config", "user.email", "t@example.com")
    git("config", "user.name", "t")
    (tmp_path / "ada.py").write_text(GOOD)
    git("add", ".")
    git("commit", "-qm", "add", when="2026-01-01T00:00:00")
    git("rm", "-q", "ada.py")
    git("commit", "-qm", "remove", when="2026-01-02T00:00:00")
    (tmp_path / "ada.py").write_text(GOOD)
    git("add", ".")
    git("commit", "-qm", "add again", when="2026-01-03T00:00:00")
    assert wall.added_time(tmp_path / "ada.py") == int(git("log", "-1", "--format=%ct"))
