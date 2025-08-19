import uuid
import pytest

from nadooit_website.services import check__session_id__is_valid


def test_check_session_id_invalid_string_returns_false():
    assert check__session_id__is_valid("not-a-uuid") is False


def test_check_session_id_injection_like_returns_false():
    bad = "abcd' OR '1'='1"
    assert check__session_id__is_valid(bad) is False


def test_check_session_id_wrong_type_returns_false():
    assert check__session_id__is_valid(12345) is False
    assert check__session_id__is_valid(None) is False
    assert check__session_id__is_valid(b"bytes") is False
