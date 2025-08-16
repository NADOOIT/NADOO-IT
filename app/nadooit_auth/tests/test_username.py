from nadooit_auth.username import get__new_username


def test_get__new_username_generates_20_alnum_chars():
    u = get__new_username()
    assert isinstance(u, str)
    assert len(u) == 20
    assert u.isalnum()


def test_get__new_username_is_random():
    u1 = get__new_username()
    u2 = get__new_username()
    assert u1 != u2
    assert len(u1) == 20 and len(u2) == 20
