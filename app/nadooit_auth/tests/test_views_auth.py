import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from nadooit_hr.models import Employee


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(
        username="tester", email="t@example.com", password="pw", is_active=True
    )

@pytest.fixture
def employee(db, user):
    return Employee.objects.create(user=user)


def test_login_get_renders(db, client):
    resp = client.get(reverse("nadooit_auth:login-user"))
    assert resp.status_code == 200


def test_login_post_invalid_redirects_to_login(db, client, monkeypatch):
    # Force authenticate to return None (invalid code)
    import nadooit_auth.views as auth_views

    monkeypatch.setattr(auth_views, "authenticate", lambda request, user_code: None)
    resp = client.post(reverse("nadooit_auth:login-user"), {"user_code": "bad"})
    assert resp.status_code in (301, 302)
    assert resp.url.endswith("/auth/login-user")


def test_login_post_valid_redirects_to_os(db, client, user, monkeypatch):
    import nadooit_auth.views as auth_views

    # authenticate returns a user object marked active
    monkeypatch.setattr(auth_views, "authenticate", lambda request, user_code: user)
    resp = client.post(reverse("nadooit_auth:login-user"), {"user_code": "ok"})
    assert resp.status_code in (301, 302)
    # login_user redirects to /nadooit-os on success when no next is provided
    assert resp.url.endswith("/nadooit-os")


def test_logout_redirects_to_login(db, client):
    resp = client.get(reverse("nadooit_auth:logout-user"))
    assert resp.status_code in (301, 302)
    assert resp.url.endswith("/auth/login-user")


def test_register_requires_keymanager_permission(db, client, user, employee, monkeypatch):
    # Anonymous -> redirected
    resp = client.get(reverse("nadooit_auth:register-user"))
    assert resp.status_code in (301, 302)
    assert "login-user" in resp.url

    # Logged-in but without permission -> still redirected (user_passes_test)
    client.force_login(user)
    resp = client.get(reverse("nadooit_auth:register-user"))
    assert resp.status_code in (301, 302)

    # Create a real KeyManager entry for the employee so the decorator check passes
    from nadooit_key.models import KeyManager

    KeyManager.objects.create(user=employee, can_create_keys=True)
    resp = client.get(reverse("nadooit_auth:register-user"))
    assert resp.status_code == 200
