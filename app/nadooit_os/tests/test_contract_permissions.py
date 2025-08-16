import pytest
from django.urls import reverse
from model_bakery import baker
from uuid import uuid4

from nadooit_hr.models import EmployeeContract, EmployeeManagerContract


@pytest.mark.django_db
def test_deactivate_contract_denied_for_manager_of_other_customer(client):
    # Setup: two customers, manager tied to customer A, target contract under customer B
    customer_a = baker.make("nadooit_crm.Customer")
    customer_b = baker.make("nadooit_crm.Customer")

    manager_user = baker.make("nadooit_auth.User")
    manager_employee = baker.make("nadooit_hr.Employee", user=manager_user)
    manager_contract = baker.make(
        EmployeeContract,
        employee=manager_employee,
        customer=customer_a,
        is_active=True,
    )
    baker.make(
        EmployeeManagerContract,
        contract=manager_contract,
        can_delete_employee=True,
    )

    victim_user = baker.make("nadooit_auth.User")
    victim_employee = baker.make("nadooit_hr.Employee", user=victim_user)
    target_contract = baker.make(
        EmployeeContract,
        employee=victim_employee,
        customer=customer_b,
        is_active=True,
    )

    client.force_login(manager_user)
    url = reverse("nadooit_os:deactivate-contract", args=[str(target_contract.id)])
    resp = client.post(url)

    assert resp.status_code in (401, 403), resp.content
    target_contract.refresh_from_db()
    assert target_contract.is_active is True


@pytest.mark.django_db
def test_deactivate_contract_404_on_unknown_id(client):
    customer = baker.make("nadooit_crm.Customer")

    # Manager with delete ability for this customer
    manager_user = baker.make("nadooit_auth.User")
    manager_employee = baker.make("nadooit_hr.Employee", user=manager_user)
    manager_contract = baker.make(
        EmployeeContract,
        employee=manager_employee,
        customer=customer,
        is_active=True,
    )
    baker.make(
        EmployeeManagerContract,
        contract=manager_contract,
        can_delete_employee=True,
    )

    client.force_login(manager_user)
    url = reverse("nadooit_os:deactivate-contract", args=[str(uuid4())])
    resp = client.post(url)
    assert resp.status_code == 404


@pytest.mark.django_db
def test_activate_contract_404_on_unknown_id(client):
    customer = baker.make("nadooit_crm.Customer")

    # Manager with delete ability for this customer
    manager_user = baker.make("nadooit_auth.User")
    manager_employee = baker.make("nadooit_hr.Employee", user=manager_user)
    manager_contract = baker.make(
        EmployeeContract,
        employee=manager_employee,
        customer=customer,
        is_active=True,
    )
    baker.make(
        EmployeeManagerContract,
        contract=manager_contract,
        can_delete_employee=True,
    )

    client.force_login(manager_user)
    url = reverse("nadooit_os:activate-contract", args=[str(uuid4())])
    resp = client.post(url)
    assert resp.status_code == 404


@pytest.mark.django_db
def test_activate_contract_denied_without_delete_ability(client):
    customer = baker.make("nadooit_crm.Customer")

    manager_user = baker.make("nadooit_auth.User")
    manager_employee = baker.make("nadooit_hr.Employee", user=manager_user)
    manager_contract = baker.make(
        EmployeeContract,
        employee=manager_employee,
        customer=customer,
        is_active=True,
    )
    # Manager lacks can_delete_employee
    baker.make(
        EmployeeManagerContract,
        contract=manager_contract,
        can_delete_employee=False,
    )

    victim_user = baker.make("nadooit_auth.User")
    victim_employee = baker.make("nadooit_hr.Employee", user=victim_user)
    target_contract = baker.make(
        EmployeeContract,
        employee=victim_employee,
        customer=customer,
        is_active=False,
    )

    client.force_login(manager_user)
    url = reverse("nadooit_os:activate-contract", args=[str(target_contract.id)])
    resp = client.post(url)

    assert resp.status_code in (401, 403), resp.content
    target_contract.refresh_from_db()
    assert target_contract.is_active is False


@pytest.mark.django_db
def test_manager_can_modify_contract_for_same_customer(client):
    customer = baker.make("nadooit_crm.Customer")

    manager_user = baker.make("nadooit_auth.User")
    manager_employee = baker.make("nadooit_hr.Employee", user=manager_user)
    manager_contract = baker.make(
        EmployeeContract,
        employee=manager_employee,
        customer=customer,
        is_active=True,
    )
    baker.make(
        EmployeeManagerContract,
        contract=manager_contract,
        can_delete_employee=True,
    )

    victim_user = baker.make("nadooit_auth.User")
    victim_employee = baker.make("nadooit_hr.Employee", user=victim_user)
    target_contract = baker.make(
        EmployeeContract,
        employee=victim_employee,
        customer=customer,
        is_active=True,
    )

    client.force_login(manager_user)
    # Deactivate
    url_deact = reverse("nadooit_os:deactivate-contract", args=[str(target_contract.id)])
    resp = client.post(url_deact)
    assert resp.status_code == 200
    target_contract.refresh_from_db()
    assert target_contract.is_active is False

    # Activate
    url_act = reverse("nadooit_os:activate-contract", args=[str(target_contract.id)])
    resp2 = client.post(url_act)
    assert resp2.status_code == 200
    target_contract.refresh_from_db()
    assert target_contract.is_active is True
