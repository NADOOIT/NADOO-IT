import uuid
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from nadooit_crm.models import Customer
from nadooit_hr.models import Employee, EmployeeContract, EmployeeManagerContract


@pytest.fixture
def user_with_employee(db):
    User = get_user_model()
    u = User.objects.create_user(
        username="mgr", email="mgr@example.com", password="pw", is_active=True
    )
    e = Employee.objects.create(user=u)
    return u, e


@pytest.fixture
def other_user_with_employee(db):
    User = get_user_model()
    u = User.objects.create_user(
        username="emp", email="emp@example.com", password="pw", is_active=True
    )
    e = Employee.objects.create(user=u)
    return u, e


@pytest.fixture
def customer(db):
    return Customer.objects.create(name="Acme")


@pytest.fixture
def employee_contract(db, other_user_with_employee, customer):
    _, employee = other_user_with_employee
    return EmployeeContract.objects.create(employee=employee, customer=customer)


def test_deactivate_contract_get_not_allowed(db, client, user_with_employee, employee_contract):
    user, _ = user_with_employee
    client.force_login(user)
    url = reverse(
        "nadooit_os:deactivate-contract", args=[str(employee_contract.id)]
    )
    resp = client.get(url)
    assert resp.status_code == 405


def test_deactivate_contract_requires_permission(db, client, user_with_employee, employee_contract):
    user, _ = user_with_employee
    client.force_login(user)
    # No EmployeeManagerContract for this customer -> 403
    url = reverse(
        "nadooit_os:deactivate-contract", args=[str(employee_contract.id)]
    )
    resp = client.post(url)
    assert resp.status_code == 403
    employee_contract.refresh_from_db()
    assert employee_contract.is_active is True


def test_deactivate_contract_cross_customer_403(
    db, client, user_with_employee, employee_contract
):
    user, mgr_employee = user_with_employee
    client.force_login(user)

    # Manager has rights for a different customer
    other_customer = Customer.objects.create(name="OtherCo")
    mgr_base_contract = EmployeeContract.objects.create(
        employee=mgr_employee, customer=other_customer
    )
    EmployeeManagerContract.objects.create(
        contract=mgr_base_contract, can_delete_employee=True
    )

    url = reverse(
        "nadooit_os:deactivate-contract", args=[str(employee_contract.id)]
    )
    resp = client.post(url)
    assert resp.status_code == 403
    employee_contract.refresh_from_db()
    assert employee_contract.is_active is True


def test_activate_contract_cross_customer_403(
    db, client, user_with_employee, employee_contract
):
    # Deactivate target first
    employee_contract.is_active = False
    employee_contract.save()

    user, mgr_employee = user_with_employee
    client.force_login(user)

    # Manager has rights for a different customer
    other_customer = Customer.objects.create(name="OtherCo")
    mgr_base_contract = EmployeeContract.objects.create(
        employee=mgr_employee, customer=other_customer
    )
    EmployeeManagerContract.objects.create(
        contract=mgr_base_contract, can_delete_employee=True
    )

    url = reverse(
        "nadooit_os:activate-contract", args=[str(employee_contract.id)]
    )
    resp = client.post(url)
    assert resp.status_code == 403
    employee_contract.refresh_from_db()
    assert employee_contract.is_active is False


def test_deactivate_contract_unknown_id_404(db, client, user_with_employee, customer):
    user, mgr_employee = user_with_employee
    client.force_login(user)

    # Grant rights for some customer, but target ID doesn't exist
    mgr_base_contract = EmployeeContract.objects.create(
        employee=mgr_employee, customer=customer
    )
    EmployeeManagerContract.objects.create(
        contract=mgr_base_contract, can_delete_employee=True
    )

    unknown_id = uuid.uuid4()
    url = reverse("nadooit_os:deactivate-contract", args=[str(unknown_id)])
    resp = client.post(url)
    assert resp.status_code == 404


@pytest.mark.parametrize(
    "bad_id",
    [
        "' OR '1'='1",
        "1; DROP TABLE employee_contract;",
        "not-a-uuid",
    ],
)
def test_deactivate_contract_injection_like_id_404(db, client, user_with_employee, customer, bad_id):
    user, mgr_employee = user_with_employee
    client.force_login(user)

    # Grant rights for some customer
    mgr_base_contract = EmployeeContract.objects.create(
        employee=mgr_employee, customer=customer
    )
    EmployeeManagerContract.objects.create(
        contract=mgr_base_contract, can_delete_employee=True
    )

    url = reverse("nadooit_os:deactivate-contract", args=[bad_id])
    resp = client.post(url)
    assert resp.status_code == 404


@pytest.mark.parametrize(
    "bad_id",
    [
        "' OR '1'='1",
        "1; DROP TABLE employee_contract;",
        "not-a-uuid",
    ],
)
def test_activate_contract_injection_like_id_404(db, client, user_with_employee, customer, bad_id):
    user, mgr_employee = user_with_employee
    client.force_login(user)

    # Grant rights for some customer
    mgr_base_contract = EmployeeContract.objects.create(
        employee=mgr_employee, customer=customer
    )
    EmployeeManagerContract.objects.create(
        contract=mgr_base_contract, can_delete_employee=True
    )

    url = reverse("nadooit_os:activate-contract", args=[bad_id])
    resp = client.post(url)
    assert resp.status_code == 404


def test_activate_contract_unknown_id_404(db, client, user_with_employee, customer):
    user, mgr_employee = user_with_employee
    client.force_login(user)

    # Grant rights for some customer, but target ID doesn't exist
    mgr_base_contract = EmployeeContract.objects.create(
        employee=mgr_employee, customer=customer
    )
    EmployeeManagerContract.objects.create(
        contract=mgr_base_contract, can_delete_employee=True
    )

    unknown_id = uuid.uuid4()
    url = reverse("nadooit_os:activate-contract", args=[str(unknown_id)])
    resp = client.post(url)
    assert resp.status_code == 404


def test_deactivate_contract_happy_path(db, client, user_with_employee, employee_contract, customer):
    user, mgr_employee = user_with_employee
    client.force_login(user)

    # Grant permission for same customer with can_delete_employee
    mgr_base_contract = EmployeeContract.objects.create(
        employee=mgr_employee, customer=customer
    )
    EmployeeManagerContract.objects.create(
        contract=mgr_base_contract, can_delete_employee=True
    )

    url = reverse(
        "nadooit_os:deactivate-contract", args=[str(employee_contract.id)]
    )
    resp = client.post(url)
    assert resp.status_code == 200
    employee_contract.refresh_from_db()
    assert employee_contract.is_active is False
    assert employee_contract.deactivation_date is not None


def test_activate_contract_get_not_allowed(db, client, user_with_employee, employee_contract):
    user, _ = user_with_employee
    client.force_login(user)
    url = reverse(
        "nadooit_os:activate-contract", args=[str(employee_contract.id)]
    )
    resp = client.get(url)
    assert resp.status_code == 405


def test_activate_contract_requires_permission(db, client, user_with_employee, employee_contract):
    # First deactivate so activation path is meaningful
    employee_contract.is_active = False
    employee_contract.save()

    user, _ = user_with_employee
    client.force_login(user)

    url = reverse(
        "nadooit_os:activate-contract", args=[str(employee_contract.id)]
    )
    resp = client.post(url)
    assert resp.status_code == 403
    employee_contract.refresh_from_db()
    assert employee_contract.is_active is False


def test_activate_contract_happy_path(db, client, user_with_employee, employee_contract, customer):
    # Deactivate first
    employee_contract.is_active = False
    employee_contract.save()

    user, mgr_employee = user_with_employee
    client.force_login(user)

    # Grant permission for same customer with can_delete_employee
    mgr_base_contract = EmployeeContract.objects.create(
        employee=mgr_employee, customer=customer
    )
    EmployeeManagerContract.objects.create(
        contract=mgr_base_contract, can_delete_employee=True
    )

    url = reverse(
        "nadooit_os:activate-contract", args=[str(employee_contract.id)]
    )
    resp = client.post(url)
    assert resp.status_code == 200
    employee_contract.refresh_from_db()
    assert employee_contract.is_active is True
