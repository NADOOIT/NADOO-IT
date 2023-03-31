import uuid
import pytest
from model_bakery import baker


@pytest.mark.django_db
def test_check__session_id__is_valid():

    session_id = uuid.uuid4()

    session = baker.make("nadooit_website.Session", session_id=session_id)

    assert session.session_id == session_id
