import uuid
import pytest
from model_bakery import baker

from nadooit_website.services import (
    check__session_id__is_valid,
    get__session_tick,
    received__session_still_active_signal__for__session_id,
    add__signal,
    create__session,
)
import nadooit_website.services as website_services
from nadooit_website.models import Session

@pytest.mark.django_db
def test_check__session_id__is_valid():
    valid_session = baker.make("nadooit_website.Session")
    assert check__session_id__is_valid(valid_session.session_id) is True
    assert check__session_id__is_valid(uuid.uuid4()) is False

def test_get__session_tick_returns_5():
    # Act
    tick = get__session_tick()
    # Assert
    assert isinstance(tick, int)
    assert tick == 5

@pytest.mark.django_db
def test_received__session_still_active_signal__increments_duration():
    # Arrange
    session: Session = baker.make("nadooit_website.Session", session_duration=0)
    # Act
    returned_id = received__session_still_active_signal__for__session_id(
        session.session_id
    )
    session.refresh_from_db()
    # Assert
    assert returned_id == session.session_id
    assert session.session_duration == get__session_tick()

def test_add__signal_click_injects_expected_script():
    # Arrange
    html = "<div>content</div>"
    session_id = "sid"
    section_id = "sec"
    # Act
    out = add__signal(html, session_id, section_id, "click")
    # Assert
    assert f'data-session-id="{session_id}"' in out
    assert f'data-section-id="{section_id}"' in out
    assert "fetch('/signal/" in out

def test_add__signal_mouseleave_contains_interaction_time():
    # Act
    out = add__signal("<p>x</p>", "sid", "sec", "mouseleave")
    # Assert
    assert "mouseenter" in out
    assert "mouseleave" in out
    assert "interactionTime" in out
    assert "fetch('/signal/" in out

def test_add__signal_end_of_session_sections_wraps_html():
    # Act
    out = add__signal("<span>ok</span>", uuid.uuid4(), uuid.uuid4(), "end_of_session_sections")
    # Assert
    assert 'class="banner"' in out
    assert "end_of_session" in out

@pytest.mark.django_db
def test_create__session_creates_session_with_section_order(monkeypatch):
    # Arrange: ensure get_most_successful_section_order returns a valid Section_Order
    def fake_get_most_successful_section_order():
        return baker.make("nadooit_website.Section_Order")

    monkeypatch.setattr(
        website_services, "get_most_successful_section_order", fake_get_most_successful_section_order
    )
    # Act
    new_session_id = create__session()
    # Assert
    assert Session.objects.filter(session_id=new_session_id).exists()
    s = Session.objects.get(session_id=new_session_id)
    assert s.session_section_order is not None
    # current implementation forces variant to "control"
    assert getattr(s, "variant", "control") == "control"
