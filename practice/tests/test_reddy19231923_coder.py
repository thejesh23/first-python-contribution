from greetings.reddy19231923_coder import greet


def test_greet_includes_name():
    assert "Sam" in greet("Sam")
