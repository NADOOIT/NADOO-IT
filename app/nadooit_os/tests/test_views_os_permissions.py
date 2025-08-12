import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from nadooit_hr.models import Employee
from nadooit_crm.models import Customer


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(
        username="osuser", email="os@example.com", password="pw", is_active=True
    )

@pytest.fixture
def employee(db, user):
    return Employee.objects.create(user=user)


@pytest.fixture
def normal_user(db):
    """Local normal_user fixture that also creates an Employee for the user.
    Many OS views access request.user.employee; without this, posts would error.
    """
    User = get_user_model()
    u = User.objects.create_user(
        username="normal", email="normal@example.com", password="pw", is_active=True
    )
    Employee.objects.create(user=u)
    return u


def test_index_requires_login(db, client, user, employee):
    # anon -> redirect to login
    resp = client.get(reverse("nadooit_os:nadooit-os"))
    assert resp.status_code in (301, 302)
    assert "login-user" in resp.url

    # logged in -> ok
    client.force_login(user)
    resp = client.get(reverse("nadooit_os:nadooit-os"))
    assert resp.status_code == 200


def test_create_api_key_permissions(db, client, user, employee, monkeypatch):
    url = reverse("nadooit_os:create-api-key")

    # anon -> redirect
    resp = client.get(url)
    assert resp.status_code in (301, 302)
    assert "login-user" in resp.url

    # logged in without permission -> 403 (inline authorization)
    client.force_login(user)
    resp = client.get(url)
    assert resp.status_code == 403

    # with permission -> 200 (create ApiKeyManager relation on employee)
    from nadooit_api_key.models import NadooitApiKeyManager

    NadooitApiKeyManager.objects.create(employee=employee)
    resp = client.get(url)
    assert resp.status_code == 200


def test_revoke_api_key_requires_login(db, client, user, employee):
    url = reverse("nadooit_os:revoke-api-key")

    # anon -> redirect
    resp = client.get(url)
    assert resp.status_code in (301, 302)
    assert "login-user" in resp.url

    # logged in -> ok
    client.force_login(user)
    resp = client.get(url)
    assert resp.status_code == 200


def test_create_api_key_post_non_manager_redirects(db, client, user, employee):
    import uuid

    client.force_login(user)
    url = reverse("nadooit_os:create-api-key")
    # POST as non-manager should be forbidden (inline authorization)
    resp = client.post(url, data={"api_key": str(uuid.uuid4())})
    assert resp.status_code == 403


def test_create_api_key_post_manager_creates_and_hashes(db, client, user, employee):
    import uuid
    import hashlib
    from nadooit_api_key.models import NadooitApiKey, NadooitApiKeyManager

    # make user an ApiKeyManager (no per-flag check in view)
    NadooitApiKeyManager.objects.create(employee=employee)

    client.force_login(user)
    url = reverse("nadooit_os:create-api-key")
    raw_key = uuid.uuid4()

    resp = client.post(url, data={"api_key": str(raw_key)})
    # view redirects to submitted=True
    assert resp.status_code in (301, 302)
    assert "submitted=True" in resp.url

    # A new active key exists for the user and is stored hashed
    keys = NadooitApiKey.objects.filter(user=user, is_active=True)
    assert keys.count() == 1
    stored = keys.first().api_key
    assert stored != str(raw_key)
    assert stored == hashlib.sha256(str(raw_key).encode()).hexdigest()


def test_revoke_api_key_post_affects_only_request_user(db, client, user, employee):
    from nadooit_os.services import create__NadooitApiKey__for__user
    from nadooit_api_key.models import NadooitApiKey

    # second user
    User = get_user_model()
    other = User.objects.create_user(
        username="osuser2", email="os2@example.com", password="pw", is_active=True
    )
    other_emp = Employee.objects.create(user=other)

    # create keys for both users
    k1 = create__NadooitApiKey__for__user(user)
    k2 = create__NadooitApiKey__for__user(other)

    # sanity
    assert NadooitApiKey.objects.filter(user=user, is_active=True).count() == 1
    assert NadooitApiKey.objects.filter(user=other, is_active=True).count() == 1

    # revoke as user1
    client.force_login(user)
    url = reverse("nadooit_os:revoke-api-key")
    resp = client.post(url)
    assert resp.status_code in (301, 302)
    assert "submitted=True" in resp.url

    # user1 keys inactive, user2 keys unaffected
    assert NadooitApiKey.objects.filter(user=user, is_active=True).count() == 0
    assert NadooitApiKey.objects.filter(user=other, is_active=True).count() == 1


def test_all_os_routes_require_login_redirect(db, client):
    import uuid
    routes = [
        ("nadooit-os", {}),
        ("customer-time-account-overview", {}),
        ("give-customer-time-account-manager-role", {}),
        ("customer-order-overview", {}),
        (
            "customer-program-execution-filter-tabs",
            {"filter_type": "unknown", "cutomer_id": uuid.uuid4()},
        ),
        (
            "customer-program-execution-list-for-cutomer",
            {"filter_type": "unknown", "cutomer_id": uuid.uuid4()},
        ),
        (
            "export-transactions",
            {"filter_type": "unknown", "cutomer_id": uuid.uuid4()},
        ),
        (
            "customer-program-execution-list-complaint-modal",
            {"customer_program_execution_id": uuid.uuid4()},
        ),
        (
            "customer-program-execution-send-complaint",
            {"customer_program_execution_id": uuid.uuid4()},
        ),
        ("create-api-key", {}),
        ("revoke-api-key", {}),
        ("customer-program-overview", {}),
        ("customer-program-profile", {"customer_program_id": uuid.uuid4()}),
        ("give-customer-program-manager-role", {}),
        ("employee-overview", {}),
        ("my-profile", {}),
        ("add-employee", {}),
        ("give-employee-manager-role", {}),
        ("deactivate-contract", {"employee_contract_id": "x"}),
        ("activate-contract", {"employee_contract_id": "x"}),
    ]

    for name, kwargs in routes:
        url = reverse(f"nadooit_os:{name}", kwargs=kwargs)
        resp = client.get(url)
        assert resp.status_code in (301, 302)
        assert "login-user" in resp.url


def test_logged_in_non_manager_gets_403_on_sensitive_posts(db, client, normal_user):
    client.force_login(normal_user)
    # Create a real customer so guard clauses pass and we hit per-customer 403 checks
    customer = Customer.objects.create(name="Acme")

    # name, data (minimal valid payloads)
    protected_posts = [
        (
            "give-customer-time-account-manager-role",
            {"customers": str(customer.id), "user_code": normal_user.user_code},
        ),
        (
            "give-customer-program-execution-manager-role",
            {"customer_id": str(customer.id), "user_code": normal_user.user_code},
        ),
        (
            "give-customer-program-manager-role",
            {"customers": str(customer.id), "user_code": normal_user.user_code},
        ),
        (
            "give-employee-manager-role",
            {"customers": str(customer.id), "user_code": normal_user.user_code},
        ),
        (
            "add-employee",
            {"customers": str(customer.id), "user_code": normal_user.user_code},
        ),
    ]

    for name, data in protected_posts:
        url = reverse(f"nadooit_os:{name}")
        resp = client.post(url, data=data)
        assert resp.status_code == 403


def test_all_os_post_routes_require_login_redirect(db, client):
    import uuid
    # name, kwargs, data
    post_routes = [
        ("give-customer-time-account-manager-role", {}, {}),
        ("give-customer-program-execution-manager-role", {}, {}),
        ("give-customer-program-manager-role", {}, {}),
        ("give-employee-manager-role", {}, {}),
        ("add-employee", {}, {"username": "x"}),
        ("create-api-key", {}, {"api_key": str(uuid.uuid4())}),
        ("revoke-api-key", {}, {}),
        (
            "customer-program-execution-send-complaint",
            {"customer_program_execution_id": uuid.uuid4()},
            {"message": "x"},
        ),
    ]

    for name, kwargs, data in post_routes:
        url = reverse(f"nadooit_os:{name}", kwargs=kwargs)
        resp = client.post(url, data=data)
        assert resp.status_code in (301, 302)
        assert "login-user" in resp.url

