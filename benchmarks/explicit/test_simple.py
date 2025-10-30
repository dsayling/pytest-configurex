"""Explicit registration test - plugin with pytest.ini configured class."""


def test_explicit_1(configurex):
    """Test with explicitly registered settings."""
    assert configurex is not None
    assert hasattr(configurex, "custom_field")
    assert configurex.custom_field == "explicit_value"


def test_explicit_2(configurex):
    """Another test with explicit settings."""
    assert configurex.another_field == 99


def test_explicit_3(configurex):
    """Third test with explicit settings."""
    assert configurex.verbosity == 0
