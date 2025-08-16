import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from model_bakery import baker

from nadooit_website.models import Visit, Section_Order
from django.conf import settings
import os
import uuid
import nadooit_website.views as website_views


@pytest.fixture
def staff_user(db):
    User = get_user_model()
    return User.objects.create_user(
        username="staff", email="staff@example.com", password="pw", is_staff=True
    )


@pytest.fixture
def normal_user(db):
    User = get_user_model()
    return User.objects.create_user(
        username="user", email="user@example.com", password="pw", is_staff=False
    )


def test_new_index_creates_visit_and_renders(db, client, monkeypatch):
    # Avoid full session creation workflow by stubbing create__session
    monkeypatch.setattr(website_views, "create__session", lambda: uuid.uuid4())
    # Avoid complex template building in service; only need a string for context
    monkeypatch.setattr(
        website_views,
        "get__template__for__session_id",
        lambda sid: website_views.Template("<div>ok</div>"),
    )

    resp = client.get(reverse("nadooit_website:index"))
    assert resp.status_code == 200
    assert Visit.objects.filter(site="New_Index").count() == 1
    assert "session_id" in resp.context
    assert "section_entry" in resp.context


def test_impressum_creates_visit(db, client):
    resp = client.get(reverse("nadooit_website:impressum"))
    assert resp.status_code == 200
    assert Visit.objects.filter(site="Impressum").count() == 1


def test_datenschutz_creates_visit(db, client):
    resp = client.get(reverse("nadooit_website:datenschutz"))
    assert resp.status_code == 200
    assert Visit.objects.filter(site="Datenschutz").count() == 1


def test_statistics_permissions(db, client, normal_user, staff_user):
    # Anonymous -> redirected to login page
    resp = client.get(reverse("nadooit_website:statistics"))
    assert resp.status_code in (301, 302)
    assert "login-user" in resp.url

    # Authenticated non-staff -> still redirected to login-url (staff gate)
    client.force_login(normal_user)
    resp = client.get(reverse("nadooit_website:statistics"))
    assert resp.status_code in (301, 302)
    assert "login-user" in resp.url

    # Staff -> allowed
    client.force_login(staff_user)
    resp = client.get(reverse("nadooit_website:statistics"))
    assert resp.status_code == 200


def test_upload_zip_requires_login(db, client):
    resp = client.get(reverse("nadooit_website:video_upload"))
    assert resp.status_code in (301, 302)
    # login_required without explicit login_url uses settings.LOGIN_URL
    assert "/auth/login-user" in resp.url


def test_upload_zip_requires_staff(db, client, normal_user):
    client.force_login(normal_user)
    resp = client.get(reverse("nadooit_website:video_upload"))
    assert resp.status_code in (301, 302)
    # staff_member_required redirects to admin login for insufficient staff
    assert "/admin/login/" in resp.url


def test_upload_zip_staff_get_ok(db, client, staff_user):
    client.force_login(staff_user)
    resp = client.get(reverse("nadooit_website:video_upload"))
    assert resp.status_code == 200


def test_section_transitions_serves_html(db, client, tmp_path, monkeypatch):
    # Prepare a temporary BASE_DIR with required file path and an HTML file
    fake_base = tmp_path / "app"
    target_dir = fake_base / "nadooit_website" / "section_transition"
    target_dir.mkdir(parents=True)
    html_file = target_dir / "section_transitions.html"
    html_file.write_text("<html><body>ok</body></html>")

    monkeypatch.setattr(settings, "BASE_DIR", str(fake_base))

    resp = client.get(reverse("nadooit_website:section_transitions"))
    assert resp.status_code == 200
    assert resp["Content-Type"].startswith("text/html")
    
    
def test_section_transitions_filtered_serves_html(db, client, tmp_path, monkeypatch):
    fake_base = tmp_path / "app"
    target_dir = fake_base / "nadooit_website" / "section_transition"
    target_dir.mkdir(parents=True)
    html_file = target_dir / "section_transitions_groupA.html"
    html_file.write_text("<html><body>groupA</body></html>")

    monkeypatch.setattr(settings, "BASE_DIR", str(fake_base))

    resp = client.get(
        reverse("nadooit_website:section_transitions_filtered", args=["groupA"])
    )
    assert resp.status_code == 200
    assert b"groupA" in resp.content
    assert resp["Content-Type"].startswith("text/html")
