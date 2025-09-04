import uuid

import pytest
from django.test import RequestFactory
from django.urls import reverse

from nadooit_website.models import Session, Section_Order
from nadooit_website import views as website_views


@pytest.fixture
def rf():
    return RequestFactory()


def _make_htmx_request(rf, method: str, path: str):
    req = getattr(rf, method.lower())(path)
    # Simulate django-htmx middleware by setting request.htmx
    req.htmx = True
    return req


@pytest.mark.django_db
class TestGetNextSection:
    def test_non_htmx_returns_403(self, rf):
        path = reverse("nadooit_website:get_next_section", args=["invalid", "cur"])
        req = rf.get(path)
        resp = website_views.get_next_section(req, "invalid", "cur")
        assert resp.status_code == 403

    def test_htmx_invalid_session_returns_403(self, rf):
        path = reverse("nadooit_website:get_next_section", args=[str(uuid.uuid4()), "cur"]) 
        req = _make_htmx_request(rf, "get", path)
        resp = website_views.get_next_section(req, str(uuid.uuid4()), "cur")
        assert resp.status_code == 403

    def test_htmx_valid_session_renders_section_html(self, rf, monkeypatch):
        so = Section_Order.objects.create()
        s = Session.objects.create(session_section_order=so)

        # Patch where used in views
        called = {}

        def fake_get_next_html(session_id, current_section_id):
            called["args"] = (str(session_id), str(current_section_id))
            return "<div>OK_NEXT</div>"

        monkeypatch.setattr(
            website_views,
            "get__next_section_html",
            fake_get_next_html,
        )

        path = reverse("nadooit_website:get_next_section", args=[str(s.session_id), "cur"])
        req = _make_htmx_request(rf, "get", path)
        resp = website_views.get_next_section(req, str(s.session_id), "cur")
        assert resp.status_code == 200
        content = resp.content.decode("utf-8")
        assert "OK_NEXT" in content
        # Ensure the function was called with our args
        assert called["args"] == (str(s.session_id), "cur")

    def test_htmx_valid_session_no_more_sections_returns_message(self, rf, monkeypatch):
        so = Section_Order.objects.create()
        s = Session.objects.create(session_section_order=so)

        def fake_get_next_html(session_id, current_section_id):
            return None

        monkeypatch.setattr(
            website_views,
            "get__next_section_html",
            fake_get_next_html,
        )

        path = reverse("nadooit_website:get_next_section", args=[str(s.session_id), "cur"])
        req = _make_htmx_request(rf, "get", path)
        resp = website_views.get_next_section(req, str(s.session_id), "cur")
        assert resp.status_code == 200
        assert resp.content.decode("utf-8") == "No more sections available."


@pytest.mark.django_db
class TestSessionIsActiveSignal:
    def test_non_htmx_returns_403(self, rf):
        path = reverse("nadooit_website:session_is_active_signal", args=["invalid"])
        req = rf.get(path)
        resp = website_views.session_is_active_signal(req, "invalid")
        assert resp.status_code == 403

    def test_htmx_invalid_session_returns_403(self, rf):
        sid = str(uuid.uuid4())
        path = reverse("nadooit_website:session_is_active_signal", args=[sid])
        req = _make_htmx_request(rf, "get", path)
        resp = website_views.session_is_active_signal(req, sid)
        assert resp.status_code == 403

    def test_htmx_valid_session_calls_service_and_200(self, rf, monkeypatch):
        so = Section_Order.objects.create()
        s = Session.objects.create(session_section_order=so)

        called = {}

        def fake_received_signal(session_id):
            called["session_id"] = str(session_id)

        monkeypatch.setattr(
            website_views,
            "received__session_still_active_signal__for__session_id",
            fake_received_signal,
        )

        path = reverse("nadooit_website:session_is_active_signal", args=[str(s.session_id)])
        req = _make_htmx_request(rf, "get", path)
        resp = website_views.session_is_active_signal(req, str(s.session_id))
        assert resp.status_code == 200
        assert called["session_id"] == str(s.session_id)


@pytest.mark.django_db
class TestEndOfSessionSections:
    def test_non_htmx_returns_403(self, rf):
        path = reverse("nadooit_website:end_of_session_sections", args=["invalid", "cur"]) 
        req = rf.get(path)
        resp = website_views.end_of_session_sections(req, "invalid", "cur")
        assert resp.status_code == 403

    def test_htmx_invalid_session_returns_403(self, rf):
        path = reverse("nadooit_website:end_of_session_sections", args=[str(uuid.uuid4()), "cur"]) 
        req = _make_htmx_request(rf, "get", path)
        resp = website_views.end_of_session_sections(req, str(uuid.uuid4()), "cur")
        assert resp.status_code == 403

    def test_htmx_valid_session_happy_path_renders(self, rf, monkeypatch):
        so = Section_Order.objects.create()
        s = Session.objects.create(session_section_order=so)

        # Stubs for services used in the view
        class _Next:
            def __init__(self, section_id):
                self.section_id = section_id

        # Minimal fakes to satisfy the flow
        monkeypatch.setattr(website_views, "categorize_user", lambda _sid: "A")
        monkeypatch.setattr(website_views, "get_seen_sections", lambda _sid: [])
        monkeypatch.setattr(website_views, "create__session_signal__for__session_id", lambda **kwargs: None)

        # get_next_section_based_on_variant returns a dummy object with section_id
        monkeypatch.setattr(
            website_views,
            "get_next_section_based_on_variant",
            lambda session_id, current_section_id, user_category, seen_sections, variant: _Next("nxt"),
        )

        # Return simple HTML and passthrough add__signal
        monkeypatch.setattr(
            website_views,
            "get__section_html_including_signals__for__section_and_session_id",
            lambda section, session_id: "<div>OK_END</div>",
        )
        monkeypatch.setattr(website_views, "add__signal", lambda html, *_args, **_kw: html)

        # Avoid actually queuing a task; record call
        called = {}
        class _DummyTask:
            def delay(self, sess_id, sec_id):
                called["args"] = (str(sess_id), str(sec_id))

        monkeypatch.setattr(website_views, "update_session_section_order", _DummyTask())

        path = reverse("nadooit_website:end_of_session_sections", args=[str(s.session_id), "cur"]) 
        req = _make_htmx_request(rf, "get", path)
        resp = website_views.end_of_session_sections(req, str(s.session_id), "cur")
        assert resp.status_code == 200
        html = resp.content.decode("utf-8")
        assert "OK_END" in html
        assert called["args"] == (str(s.session_id), "nxt")

    def test_htmx_valid_session_no_more_sections_message(self, rf, monkeypatch):
        so = Section_Order.objects.create()
        s = Session.objects.create(session_section_order=so)

        monkeypatch.setattr(website_views, "categorize_user", lambda _sid: "A")
        monkeypatch.setattr(website_views, "get_seen_sections", lambda _sid: [])
        monkeypatch.setattr(website_views, "create__session_signal__for__session_id", lambda **kwargs: None)

        # Return None to trigger the "No more sections" branch
        monkeypatch.setattr(
            website_views,
            "get_next_section_based_on_variant",
            lambda *args, **kwargs: None,
        )

        path = reverse("nadooit_website:end_of_session_sections", args=[str(s.session_id), "cur"]) 
        req = _make_htmx_request(rf, "get", path)
        resp = website_views.end_of_session_sections(req, str(s.session_id), "cur")
        assert resp.status_code == 200
        assert resp.content.decode("utf-8") == "No more sections available."
