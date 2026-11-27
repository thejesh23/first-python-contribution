from greetings.karthikaun import greet


def test_greet_includes_name():
    assert "Sam" in greet("Sam")


def test_greet_empty_name_returns_string():
    assert isinstance(greet(""), str)
