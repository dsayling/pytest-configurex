"""Autodiscovery test - plugin with custom settings class (auto-discovered)."""


def test_autodiscovery_1(configurex):
    """Test with auto-discovered custom settings."""
    assert configurex is not None
    assert hasattr(configurex, "custom_field")
    assert configurex.custom_field == "benchmark_value"


def test_autodiscovery_2(configurex):
    """Another test with custom settings."""
    assert configurex.another_field == 42


def test_autodiscovery_3(configurex):
    """Third test with custom settings."""
    assert configurex.verbosity == 0
