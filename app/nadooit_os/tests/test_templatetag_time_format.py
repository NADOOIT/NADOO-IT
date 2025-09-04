import pytest

from nadooit_os.templatetags.get_time_as_string_in_hour_format_for_time_in_seconds_as_integer import (
    templatetag_get_time_as_string_in_hour_format_for_time_in_seconds_as_integer as filter_fn,
)


def test_time_format_filter_returns_dash_for_none():
    assert filter_fn(None) == "-"


def test_time_format_filter_delegates_to_helper(monkeypatch):
    calls = {}

    def fake_helper(value):
        calls["arg"] = value
        return "H:MM"

    # Patch where the helper is USED (imported into the templatetag module),
    # not the original definition in the models module.
    monkeypatch.setattr(
        "nadooit_os.templatetags.get_time_as_string_in_hour_format_for_time_in_seconds_as_integer.get_time_as_string_in_hour_format_for_time_in_seconds_as_integer",
        fake_helper,
    )

    out = filter_fn(3660)

    assert out == "H:MM"
    assert calls["arg"] == 3660
