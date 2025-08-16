import uuid
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

from nadooit_hr.models import Employee
from nadooit_api_key.models import NadooitApiKey, NadooitApiKeyManager


@pytest.fixture
def api_key_manager(db):
    User = get_user_model()
    u = User.objects.create_user(
        username="akm", email="akm@example.com", password="pw", is_active=True
    )
    e = Employee.objects.create(user=u)
    NadooitApiKeyManager.objects.create(employee=e, can_create_api_key=True)
    return u, e


@pytest.fixture
def normal_user(db):
    User = get_user_model()
    u = User.objects.create_user(
        username="norm", email="norm@example.com", password="pw", is_active=True
    )
    e = Employee.objects.create(user=u)
    return u, e


def test_manager_get_create_api_key_renders_form(db, client, api_key_manager):
    user, _ = api_key_manager
    client.force_login(user)
    url = reverse("nadooit_os:create-api-key")
    resp = client.get(url)
    assert resp.status_code == 200
    assert b"API KEY" in resp.content or b"API" in resp.content


def test_create_api_key_invalid_form_does_not_create(db, client, api_key_manager):
    user, _ = api_key_manager
    client.force_login(user)
    url = reverse("nadooit_os:create-api-key")

    # Post clearly invalid value for api_key so form is invalid
    resp = client.post(url, data={"api_key": "not-a-uuid"})
    assert resp.status_code == 200  # stays on page, no redirect
    assert NadooitApiKey.objects.filter(user=user, is_active=True).count() == 0


def test_manager_create_api_key_hash_length_and_not_plaintext(db, client, api_key_manager):
    user, _ = api_key_manager
    client.force_login(user)
    url = reverse("nadooit_os:create-api-key")

    plain = str(uuid.uuid4())
    resp = client.post(url, data={"api_key": plain})
    # Redirect back to form with submitted flag
    assert resp.status_code in (302, 301)

    key = NadooitApiKey.objects.filter(user=user, is_active=True).first()
    assert key is not None
    # Ensure not plaintext and looks like a hash (conservative length check)
    assert key.api_key != plain
    assert len(key.api_key) >= 40


def test_revoke_api_key_get_renders_page(db, client, normal_user):
    user, _ = normal_user
    client.force_login(user)
    url = reverse("nadooit_os:revoke-api-key")
    resp = client.get(url)
    assert resp.status_code == 200
    # Title text (German) or general string should appear
    assert b"API KEY" in resp.content or b"l\xc3\xb6schen" in resp.content


def test_revoke_api_key_without_existing_keys_redirects(db, client, normal_user):
    user, _ = normal_user
    client.force_login(user)
    url = reverse("nadooit_os:revoke-api-key")

    # No keys yet; should still redirect successfully and not error
    resp = client.post(url)
    assert resp.status_code in (302, 301)
    assert NadooitApiKey.objects.filter(user=user, is_active=True).count() == 0


def test_normal_user_get_create_api_key_forbidden(db, client, normal_user):
    user, _ = normal_user
    client.force_login(user)
    url = reverse("nadooit_os:create-api-key")
    resp = client.get(url)
    assert resp.status_code == 403


def test_normal_user_post_create_api_key_forbidden(db, client, normal_user):
    user, _ = normal_user
    client.force_login(user)
    url = reverse("nadooit_os:create-api-key")
    resp = client.post(url, data={"api_key": str(uuid.uuid4())})
    assert resp.status_code == 403
    assert NadooitApiKey.objects.filter(user=user).count() == 0


def test_revoke_only_affects_caller_keys(db, client, normal_user):
    # Create two users with keys
    user_a, _ = normal_user
    User = get_user_model()
    user_b = User.objects.create_user(
        username="other", email="other@example.com", password="pw", is_active=True
    )
    Employee.objects.create(user=user_b)

    # Active keys for both
    key_a = NadooitApiKey.objects.create(user=user_a, api_key=str(uuid.uuid4()))
    key_b = NadooitApiKey.objects.create(user=user_b, api_key=str(uuid.uuid4()))

    # Sanity
    assert NadooitApiKey.objects.filter(user=user_a, is_active=True).count() == 1
    assert NadooitApiKey.objects.filter(user=user_b, is_active=True).count() == 1

    # Revoke as user A
    client.force_login(user_a)
    url = reverse("nadooit_os:revoke-api-key")
    resp = client.post(url)
    assert resp.status_code in (302, 301)

    # User A's keys inactive, user B's unaffected
    key_a.refresh_from_db()
    key_b.refresh_from_db()
    assert key_a.is_active is False
    assert key_b.is_active is True
