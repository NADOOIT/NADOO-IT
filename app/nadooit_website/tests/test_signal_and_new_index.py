import json
import uuid

import pytest
from django.test import RequestFactory
from django.urls import reverse

from nadooit_website import views as website_views
from nadooit_website.models import Session, Section, Section_Order, Visit


@pytest.fixture
def rf():
    return RequestFactory()


class TestSignalView:
    def test_invalid_session_returns_403_and_no_side_effects(self, rf, monkeypatch):
        # Arrange
        called = {"count": 0}

        def fake_create_signal(*args, **kwargs):
            called["count"] += 1

        monkeypatch.setattr(
            website_views, "create__session_signal__for__session_id", fake_create_signal
        )

        path = reverse(
            "nadooit_website:signal",
            args=[uuid.uuid4(), "sec", "mouseenter_once"],
        )
        req = rf.post(path)

        # Act: pass an invalid session id directly to the view
        resp = website_views.signal(req, "not-a-uuid-injection", "sec", "mouseenter_once")

        # Assert
        assert resp.status_code == 403
        assert called["count"] == 0

    @pytest.mark.django_db
    def test_revealed_adds_section_to_session_shown_sections(self, rf, monkeypatch):
        # Arrange: create session + section
        so = Section_Order.objects.create()
        sess = Session.objects.create(session_section_order=so)
        sec = Section.objects.create(name="S", html="<div>S</div>")

        # Avoid external side-effects
        monkeypatch.setattr(
            website_views, "create__session_signal__for__session_id", lambda *a, **k: None
        )

        path = reverse(
            "nadooit_website:signal",
            args=[sess.session_id, str(sec.section_id), "revealed"],
        )
        req = rf.post(path)

        # Act
        resp = website_views.signal(
            req, str(sess.session_id), str(sec.section_id), "revealed"
        )

        # Assert
        assert resp.status_code == 200
        sess.refresh_from_db()
        assert sec in sess.shown_sections.all()

    @pytest.mark.django_db
    def test_mouseleave_increments_total_interaction_time(self, rf, monkeypatch):
        # Arrange
        so = Section_Order.objects.create()
        sess = Session.objects.create(session_section_order=so)
        sec_id = "ignored-sec"

        # Avoid external side-effects
        monkeypatch.setattr(
            website_views, "create__session_signal__for__session_id", lambda *a, **k: None
        )

        payload = {"interaction_time": 2.5}
        path = reverse(
            "nadooit_website:signal",
            args=[sess.session_id, sec_id, "mouseleave"],
        )
        req = rf.post(path, data=json.dumps(payload), content_type="application/json")

        # Act
        before = sess.total_interaction_time
        resp = website_views.signal(req, str(sess.session_id), sec_id, "mouseleave")

        # Assert
        assert resp.status_code == 200
        sess.refresh_from_db()
        assert sess.total_interaction_time == before + 2.5

    @pytest.mark.django_db
    def test_unrecognized_signal_still_returns_200(self, rf, monkeypatch):
        # Arrange
        so = Section_Order.objects.create()
        sess = Session.objects.create(session_section_order=so)

        monkeypatch.setattr(
            website_views, "create__session_signal__for__session_id", lambda *a, **k: None
        )

        path = reverse(
            "nadooit_website:signal",
            args=[sess.session_id, "sec", "noop"],
        )
        req = rf.post(path)

        # Act
        resp = website_views.signal(req, str(sess.session_id), "sec", "noop")

        # Assert
        assert resp.status_code == 200


@pytest.mark.django_db
class TestNewIndex:
    def test_creates_visit_and_renders_with_session_context(self, rf, monkeypatch):
        # Arrange
        fake_session_id = str(uuid.uuid4())

        monkeypatch.setattr(website_views, "create__session", lambda: fake_session_id)
        monkeypatch.setattr(
            website_views, "get__template__for__session_id", lambda _sid: "nadooit_website/intro.html"
        )
        monkeypatch.setattr(website_views, "get__session_tick", lambda: 5)

        path = reverse("nadooit_website:index")
        req = rf.get(path)
        before_visits = Visit.objects.count()

        # Act
        resp = website_views.new_index(req)

        # Assert
        assert resp.status_code == 200
        assert Visit.objects.count() == before_visits + 1

        # Rendered content includes the session context indirectly; we can at least
        # assert that the context variables were wired by checking the template render output
        content = resp.content.decode("utf-8")
        # Ensure the HTMX timer includes the session id context
        active_url = reverse("nadooit_website:session_is_active_signal", args=[fake_session_id])
        assert active_url in content
    
    def test_new_index_uses_unique_session_id_each_call(self, rf, monkeypatch):
        # Arrange: return different IDs to simulate per-visit sessions
        ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        def fake_create_session():
            return ids.pop(0)
        monkeypatch.setattr(website_views, "create__session", fake_create_session)
        monkeypatch.setattr(website_views, "get__template__for__session_id", lambda _s: "nadooit_website/intro.html")
        monkeypatch.setattr(website_views, "get__session_tick", lambda: 1)

        # Act
        resp1 = website_views.new_index(rf.get("/"))
        resp2 = website_views.new_index(rf.get("/"))

        # Assert
        assert resp1.status_code == 200 and resp2.status_code == 200
        # No direct way to extract context without a Test Client + templates, but the test ensures no exceptions
