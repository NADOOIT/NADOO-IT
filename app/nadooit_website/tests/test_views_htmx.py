import json
import uuid
import pytest
from django.urls import reverse
from model_bakery import baker

from nadooit_website.models import (
    Section,
    Section_Order,
    Session,
)

import nadooit_website.views as website_views
import nadooit_website.services as services


@pytest.fixture
def htmx_client(client):
    client.defaults["HTTP_HX_REQUEST"] = "true"
    return client


@pytest.fixture
def section_order(db):
    return baker.make(Section_Order)


@pytest.fixture
def session(db, section_order):
    # Ensure create__session won’t fail on hardcoded lookup by monkeypatching order
    return baker.make(Session, session_section_order=section_order)


@pytest.fixture
def section(db):
    return baker.make(Section)


def test_end_of_session_sections_success(db, htmx_client, session, section, monkeypatch):
    # Valid session and a next section exists
    monkeypatch.setattr(
        website_views,
        "check__session_id__is_valid",
        lambda sid: True,
    )
    next_section = baker.make(Section)

    # Stub next-section selection and HTML rendering pipeline
    monkeypatch.setattr(
        website_views,
        "get_next_section_based_on_variant",
        lambda sid, cur, user_cat, seen, variant: next_section,
    )
    monkeypatch.setattr(
        website_views,
        "get__section_html_including_signals__for__section_and_session_id",
        lambda sec, sid: "<div>next</div>",
    )
    monkeypatch.setattr(website_views, "add__signal", lambda html, sid, secid, st: html)

    # Patch Celery task call
    class DummyTask:
        @staticmethod
        def delay(*args, **kwargs):
            return None

    monkeypatch.setattr(website_views, "update_session_section_order", DummyTask)

    url = reverse(
        "nadooit_website:end_of_session_sections",
        args=[str(session.session_id), str(section.section_id)],
    )
    resp = htmx_client.post(url)
    assert resp.status_code == 200
    assert b"next" in resp.content


def test_end_of_session_sections_invalid_session(db, htmx_client, session, section, monkeypatch):
    monkeypatch.setattr(website_views, "check__session_id__is_valid", lambda sid: False)
    url = reverse(
        "nadooit_website:end_of_session_sections",
        args=[str(session.session_id), str(section.section_id)],
    )
    resp = htmx_client.post(url)
    assert resp.status_code == 403


def test_end_of_session_sections_no_next(db, htmx_client, session, section, monkeypatch):
    monkeypatch.setattr(website_views, "check__session_id__is_valid", lambda sid: True)
    monkeypatch.setattr(
        website_views,
        "get_next_section_based_on_variant",
        lambda sid, cur, user_cat, seen, variant: None,
    )
    url = reverse(
        "nadooit_website:end_of_session_sections",
        args=[str(session.session_id), str(section.section_id)],
    )
    resp = htmx_client.post(url)
    assert resp.status_code == 200
    assert b"No more sections available." in resp.content


def test_get_next_section_success(db, htmx_client, session, section, monkeypatch):
    monkeypatch.setattr(website_views, "check__session_id__is_valid", lambda sid: True)
    # Return raw HTML, since the view wraps it into the standard wrapper template
    monkeypatch.setattr(website_views, "get__next_section_html", lambda sid, cur: "<div>next-section</div>")

    url = reverse(
        "nadooit_website:get_next_section",
        args=[str(session.session_id), str(section.section_id)],
    )
    resp = htmx_client.get(url)
    assert resp.status_code == 200


def test_end_of_session_sections_non_htmx_forbidden(db, client, session, section):
    url = reverse(
        "nadooit_website:end_of_session_sections",
        args=[str(session.session_id), str(section.section_id)],
    )
    resp = client.post(url)
    assert resp.status_code == 403


def test_get_next_section_invalid_session(db, htmx_client, session, section, monkeypatch):
    monkeypatch.setattr(website_views, "check__session_id__is_valid", lambda sid: False)
    url = reverse("nadooit_website:get_next_section", args=[str(session.session_id), str(section.section_id)])
    resp = htmx_client.get(url)
    assert resp.status_code == 403


def test_get_next_section_non_htmx_forbidden(db, client, session, section):
    url = reverse("nadooit_website:get_next_section", args=[str(session.session_id), str(section.section_id)])
    resp = client.get(url)
    assert resp.status_code == 403


def test_session_is_active_signal_success(db, htmx_client, session, monkeypatch):
    monkeypatch.setattr(website_views, "check__session_id__is_valid", lambda sid: True)
    called = {"ok": False}

    def _mark_active(sid):
        called["ok"] = True

    monkeypatch.setattr(
        website_views, "received__session_still_active_signal__for__session_id", _mark_active
    )

    url = reverse(
        "nadooit_website:session_is_active_signal", args=[str(session.session_id)]
    )
    resp = htmx_client.post(url)
    assert resp.status_code == 200
    assert called["ok"] is True


def test_session_is_active_signal_invalid(db, htmx_client, session, monkeypatch):
    monkeypatch.setattr(website_views, "check__session_id__is_valid", lambda sid: False)
    url = reverse(
        "nadooit_website:session_is_active_signal", args=[str(session.session_id)]
    )
    resp = htmx_client.post(url)
    assert resp.status_code == 403


def test_session_is_active_signal_non_htmx_forbidden(db, client, session):
    url = reverse("nadooit_website:session_is_active_signal", args=[str(session.session_id)])
    resp = client.post(url)
    assert resp.status_code == 403


def test_signal_endpoint_various_types(db, htmx_client, session, section, monkeypatch):
    # Allow any session
    monkeypatch.setattr(website_views, "check__session_id__is_valid", lambda sid: True)

    created = {"calls": []}

    def _create(session_id, section_id, signal_type):
        created["calls"].append((str(session_id), str(section_id), signal_type))

    monkeypatch.setattr(
        website_views, "create__session_signal__for__session_id", _create
    )

    # revealed should add section to shown_sections and save session
    url = reverse(
        "nadooit_website:signal",
        args=[str(session.session_id), str(section.section_id), "revealed"],
    )
    resp = htmx_client.post(url)
    assert resp.status_code == 200

    # mouseenter_once
    url = reverse(
        "nadooit_website:signal",
        args=[str(session.session_id), str(section.section_id), "mouseenter_once"],
    )
    resp = htmx_client.post(url)
    assert resp.status_code == 200

    # mouseleave with body
    url = reverse(
        "nadooit_website:signal",
        args=[str(session.session_id), str(section.section_id), "mouseleave"],
    )
    body = {"interaction_time": 1.5}
    resp = htmx_client.post(url, data=json.dumps(body), content_type="application/json")
    assert resp.status_code == 200

    # upvote/downvote
    for sig in ("upvote", "downvote"):
        url = reverse(
            "nadooit_website:signal",
            args=[str(session.session_id), str(section.section_id), sig],
        )
        resp = htmx_client.post(url)
        assert resp.status_code == 200

    # Ensure create__session_signal__for__session_id was called for each
    assert len(created["calls"]) == 5


def test_signal_endpoint_invalid_session(db, htmx_client, session, section, monkeypatch):
    monkeypatch.setattr(website_views, "check__session_id__is_valid", lambda sid: False)
    url = reverse(
        "nadooit_website:signal",
        args=[str(session.session_id), str(section.section_id), "revealed"],
    )
    resp = htmx_client.post(url)
    assert resp.status_code == 403
