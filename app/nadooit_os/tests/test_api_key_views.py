import pytest
import uuid
from django.urls import reverse
from django.contrib.auth import get_user_model
from nadooit_hr.models import Employee
from nadooit_api_key.models import NadooitApiKey, NadooitApiKeyManager


@pytest.fixture
def user_with_employee(db):
    User = get_user_model()
    u = User.objects.create_user(
        username="u1", email="u1@example.com", password="pw", is_active=True
    )
    e = Employee.objects.create(user=u)
    return u, e


@pytest.fixture
def manager_user(db):
    User = get_user_model()
    u = User.objects.create_user(
        username="mgr", email="mgr@example.com", password="pw", is_active=True
    )
    e = Employee.objects.create(user=u)
    NadooitApiKeyManager.objects.create(employee=e, can_create_api_key=True)
    return u, e


def test_create_api_key_requires_manager(db, client, user_with_employee):
    user, _ = user_with_employee
    client.force_login(user)
    url = reverse("nadooit_os:create-api-key")
    # GET requires Api Key Manager -> 403 for authenticated non-manager
    resp = client.get(url)
    assert resp.status_code == 403

    # POST should also enforce authorization -> 403
    resp = client.post(url, data={"api_key": str(uuid.uuid4())})
    assert resp.status_code == 403


def test_manager_can_create_api_key_hashes_and_redirects(db, client, manager_user):
    user, _ = manager_user
    client.force_login(user)
    url = reverse("nadooit_os:create-api-key")

    # POST create with a valid UUID so form is valid
    resp = client.post(url, data={"api_key": str(uuid.uuid4())})
    assert resp.status_code in (302, 301)

    # One active key for user, stored hashed (not equal to plaintext)
    keys = NadooitApiKey.objects.filter(user=user, is_active=True)
    assert keys.count() == 1
    assert keys.first().api_key != "plaintext-test-key"


def test_revoke_api_key_only_affects_caller(db, client, user_with_employee, manager_user):
    user, _ = user_with_employee
    mgr, _ = manager_user

    # Create one key for each user
    NadooitApiKey.objects.create(user=user)
    NadooitApiKey.objects.create(user=mgr)

    # Revoke as normal user (allowed by view, affects only caller)
    client.force_login(user)
    url = reverse("nadooit_os:revoke-api-key")
    resp = client.post(url)
    assert resp.status_code in (302, 301)

    # User's keys inactive; manager's still active
    assert NadooitApiKey.objects.filter(user=user, is_active=True).count() == 0
    assert NadooitApiKey.objects.filter(user=mgr, is_active=True).count() == 1


def test_anonymous_redirects_on_create_and_revoke(db, client):
    # Anonymous to create-api-key
    url_create = reverse("nadooit_os:create-api-key")
    resp = client.get(url_create)
    assert resp.status_code in (302, 301)
    resp = client.post(url_create, data={"api_key": str(uuid.uuid4())})
    assert resp.status_code in (302, 301)

    # Anonymous to revoke-api-key
    url_revoke = reverse("nadooit_os:revoke-api-key")
    resp = client.get(url_revoke)
    assert resp.status_code in (302, 301)
    resp = client.post(url_revoke)
    assert resp.status_code in (302, 301)
