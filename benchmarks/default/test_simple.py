"""Default test - plugin with default settings."""


def test_default_1(configurex):
    """Test with configurex fixture."""
    assert configurex is not None
    assert configurex.verbosity == 0


def test_default_2(configurex):
    """Another test with configurex."""
    assert configurex.log_level is None


def test_default_3(configurex):
    """Third test with configurex."""
    assert configurex.markers is None
