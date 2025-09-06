import uuid

import pytest

from nadooit_website.models import Session, Section_Order
from nadooit_website.services import check__session_id__is_valid


@pytest.mark.parametrize(
    "value",
    [None, 0, 1, 1.2, object(), [], {}, "abc", "not-a-uuid", "", b"bytes"],
)
def test_check_session_id_is_valid_rejects_invalid_inputs(value):
    assert check__session_id__is_valid(value) is False


@pytest.mark.django_db
@pytest.mark.parametrize("use_str", [True, False])
def test_check_session_id_is_valid_true_when_session_exists(use_str):
    sid = uuid.uuid4()
    so = Section_Order.objects.create()
    Session.objects.create(session_id=sid, session_section_order=so)

    arg = str(sid) if use_str else sid
    assert check__session_id__is_valid(arg) is True


@pytest.mark.django_db
def test_check_session_id_is_valid_false_when_session_missing():
    # Valid UUID but no DB row
    sid = uuid.uuid4()
    assert check__session_id__is_valid(sid) is False
