import uuid
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

from nadooit_hr.models import Employee, EmployeeContract, EmployeeManagerContract
from nadooit_crm.models import Customer


@pytest.fixture
def user_and_employee(db):
    User = get_user_model()
    u = User.objects.create_user(
        username="u_norm", email="u_norm@example.com", password="pw", is_active=True
    )
    e = Employee.objects.create(user=u)
    return u, e


@pytest.fixture
def customer(db):
    return Customer.objects.create(name="Acme")


@pytest.fixture
def manager_user(db, customer):
    User = get_user_model()
    u = User.objects.create_user(
        username="mgr2", email="mgr2@example.com", password="pw", is_active=True
    )
    e = Employee.objects.create(user=u)
    # Base employee contract to grant manager abilities for this customer
    base = EmployeeContract.objects.create(employee=e, customer=customer)
    EmployeeManagerContract.objects.create(contract=base, can_delete_employee=True)
    return u, e


@pytest.fixture
def target_employee_contract(db, customer):
    # Create a separate employee and a contract we can activate/deactivate
    User = get_user_model()
    u = User.objects.create_user(
        username="target", email="target@example.com", password="pw", is_active=True
    )
    e = Employee.objects.create(user=u)
    return EmployeeContract.objects.create(employee=e, customer=customer)


def test_hr_deactivate_activate_get_method_not_allowed(db, client, manager_user, target_employee_contract):
    user, _ = manager_user
    client.force_login(user)

    # Deactivate: GET -> 405
    url = reverse("nadooit_os:deactivate-contract", args=[str(target_employee_contract.id)])
    resp = client.get(url)
    assert resp.status_code == 405

    # Activate: GET -> 405
    url = reverse("nadooit_os:activate-contract", args=[str(target_employee_contract.id)])
    resp = client.get(url)
    assert resp.status_code == 405


def test_export_transactions_post_method_not_allowed(db, client, user_and_employee, customer):
    user, _ = user_and_employee
    client.force_login(user)

    url = reverse("nadooit_os:export-transactions", args=["unpaid", customer.id])
    resp = client.post(url)
    assert resp.status_code == 405


def test_get_customer_program_profile_get_method_not_allowed(db, client, user_and_employee):
    user, _ = user_and_employee
    client.force_login(user)

    # Use a random UUID, the method check should short-circuit before other checks
    random_program_id = str(uuid.uuid4())
    url = reverse("nadooit_os:customer-program-profile", args=[random_program_id])
    resp = client.get(url)
    assert resp.status_code == 405


@pytest.mark.parametrize(
    "route_name",
    [
        "employee-overview",
        "customer-program-overview",
        "customer-time-account-overview",
        "customer-order-overview",
    ],
)
def test_overview_pages_require_correct_role__anonymous_redirects(db, client, route_name):
    # Anonymous should be redirected to login for protected pages
    url = reverse(f"nadooit_os:{route_name}")
    resp = client.get(url)
    assert resp.status_code in (302, 301)


@pytest.mark.parametrize(
    "route_name",
    [
        "employee-overview",
        "customer-program-overview",
        "customer-time-account-overview",
        "customer-order-overview",
    ],
)
def test_overview_pages_require_correct_role__logged_in_but_unauthorized_redirects(db, client, user_and_employee, route_name):
    # Logged-in user without the specific role should be redirected by user_passes_test
    user, _ = user_and_employee
    client.force_login(user)
    url = reverse(f"nadooit_os:{route_name}")
    resp = client.get(url)
    assert resp.status_code in (302, 301)
