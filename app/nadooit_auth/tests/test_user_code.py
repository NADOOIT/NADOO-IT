import pytest

from nadooit_auth.user_code import get__new_user_code, check__valid_user_code


def test_get__new_user_code_generates_six_alnum_chars():
    code = get__new_user_code()
    assert isinstance(code, str)
    assert len(code) == 6
    assert code.isalnum()


@pytest.mark.parametrize(
    "value, expected",
    [
        ("Ab12Cd", True),  # valid: 6, alnum
        ("ABCDE", False),  # invalid: too short
        ("ABCDEFG", False),  # invalid: too long
        ("Ab12$%", False),  # invalid: non-alnum
    ],
)
def test_check__valid_user_code(value, expected):
    assert check__valid_user_code(value) is expected
