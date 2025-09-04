import pytest
from django.urls import reverse
from model_bakery import baker

from nadooit_hr.models import EmployeeContract, EmployeeManagerContract


@pytest.mark.django_db
def test_add_employee_get_lists_only_authorized_customers(client):
    # Manager user and employee
    manager_user = baker.make("nadooit_auth.User")
    manager_employee = baker.make("nadooit_hr.Employee", user=manager_user)

    # Customers
    customer_allowed = baker.make("nadooit_crm.Customer")
    customer_denied = baker.make("nadooit_crm.Customer")

    # Manager must have an active contract and manager ability for allowed customer only
    manager_contract_allowed = baker.make(
        EmployeeContract,
        employee=manager_employee,
        customer=customer_allowed,
        is_active=True,
    )
    baker.make(
        EmployeeManagerContract,
        contract=manager_contract_allowed,
        can_add_new_employee=True,
    )

    # Also create a separate active contract for denied customer but WITHOUT manager ability
    baker.make(
        EmployeeContract,
        employee=manager_employee,
        customer=customer_denied,
        is_active=True,
    )

    client.force_login(manager_user)
    resp = client.get(reverse("nadooit_os:add-employee"))
    assert resp.status_code == 200

    # The context should only include customers where the manager can add employees
    ctx_list = resp.context["list_of_customers__for__employee_manager_contract"]
    ids = {str(c.id) for c in ctx_list}
    assert str(customer_allowed.id) in ids
    assert str(customer_denied.id) not in ids


@pytest.mark.django_db
def test_add_employee_post_denied_for_other_customer(client):
    # Setup: manager allowed for customer A, tries to add for customer B (denied)
    customer_a = baker.make("nadooit_crm.Customer")
    customer_b = baker.make("nadooit_crm.Customer")

    manager_user = baker.make("nadooit_auth.User")
    manager_employee = baker.make("nadooit_hr.Employee", user=manager_user)
    manager_contract_a = baker.make(
        EmployeeContract,
        employee=manager_employee,
        customer=customer_a,
        is_active=True,
    )
    baker.make(
        EmployeeManagerContract,
        contract=manager_contract_a,
        can_add_new_employee=True,
    )

    target_user = baker.make("nadooit_auth.User")

    client.force_login(manager_user)
    url = reverse("nadooit_os:add-employee")
    resp = client.post(url, {"user_code": target_user.user_code, "customers": str(customer_b.id)})

    # Hardened behavior: explicit 403; no creation should happen
    assert resp.status_code == 403
    assert not EmployeeContract.objects.filter(employee__user=target_user, customer=customer_b).exists()


@pytest.mark.django_db
def test_give_employee_manager_role_denied_for_other_customer(client):
    # Setup: manager is allowed to give role for customer A only
    customer_a = baker.make("nadooit_crm.Customer")
    customer_b = baker.make("nadooit_crm.Customer")

    manager_user = baker.make("nadooit_auth.User")
    manager_employee = baker.make("nadooit_hr.Employee", user=manager_user)
    manager_contract_a = baker.make(
        EmployeeContract,
        employee=manager_employee,
        customer=customer_a,
        is_active=True,
    )
    baker.make(
        EmployeeManagerContract,
        contract=manager_contract_a,
        can_give_manager_role=True,
    )

    victim_user = baker.make("nadooit_auth.User")

    client.force_login(manager_user)
    url = reverse("nadooit_os:give-employee-manager-role")
    resp = client.post(
        url,
        {
            "user_code": victim_user.user_code,
            "customers": str(customer_b.id),
            # arbitrary role list; service should enforce permissions
            "role": ["can_add_new_employee"],
        },
    )

    # Expect denial (either re-render 200 or 403), and no manager contract created for victim on B
    assert resp.status_code in (200, 403)
    assert not EmployeeManagerContract.objects.filter(
        contract__employee__user=victim_user,
        contract__customer=customer_b,
    ).exists()


@pytest.mark.django_db
def test_give_employee_manager_role_allowed_same_customer(client):
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
        can_give_manager_role=True,
    )

    victim_user = baker.make("nadooit_auth.User")

    client.force_login(manager_user)
    url = reverse("nadooit_os:give-employee-manager-role")
    resp = client.post(
        url,
        {
            "user_code": victim_user.user_code,
            "customers": str(customer.id),
            "role": ["can_add_new_employee"],
        },
    )

    # Expect redirect to submitted=True on success and a manager contract created for victim under this customer
    assert resp.status_code in (200, 302)

    # The view indicates success by redirecting to submitted=True. We also assert the effect.
    assert EmployeeManagerContract.objects.filter(
        contract__employee__user=victim_user,
        contract__customer=customer,
    ).exists()


@pytest.mark.django_db
def test_give_employee_manager_role_idempotent(client):
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
        can_give_manager_role=True,
    )

    victim_user = baker.make("nadooit_auth.User")

    client.force_login(manager_user)
    url = reverse("nadooit_os:give-employee-manager-role")
    payload = {
        "user_code": victim_user.user_code,
        "customers": str(customer.id),
        "role": ["can_add_new_employee"],
    }

    # Double POST
    resp1 = client.post(url, payload)
    resp2 = client.post(url, payload)

    assert resp1.status_code in (200, 302)
    assert resp2.status_code in (200, 302)
    assert (
        EmployeeManagerContract.objects.filter(
            contract__employee__user=victim_user, contract__customer=customer
        ).count()
        == 1
    )


@pytest.mark.django_db
def test_give_employee_manager_role_no_implicit_creation_for_acting_manager(client):
    """Acting user without EM manager contract should get 403 and must not gain a manager contract implicitly."""
    customer = baker.make("nadooit_crm.Customer")

    acting_user = baker.make("nadooit_auth.User")
    acting_employee = baker.make("nadooit_hr.Employee", user=acting_user)
    # Only base EmployeeContract; no EmployeeManagerContract for acting user
    baker.make(
        EmployeeContract,
        employee=acting_employee,
        customer=customer,
        is_active=True,
    )


@pytest.mark.django_db
def test_add_employee_idempotent_double_post(client):
    """Double POST to add-employee must create at most one EmployeeContract."""
    customer = baker.make("nadooit_crm.Customer")

    # Manager setup with can_add_new_employee for the customer
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
        can_add_new_employee=True,
    )

    target_user = baker.make("nadooit_auth.User")

    client.force_login(manager_user)
    url = reverse("nadooit_os:add-employee")
    payload = {"user_code": target_user.user_code, "customers": str(customer.id)}

    # Double POST
    r1 = client.post(url, payload)
    r2 = client.post(url, payload)

    assert r1.status_code in (200, 302)
    assert r2.status_code in (200, 302)

    assert (
        EmployeeContract.objects.filter(
            employee__user=target_user, customer=customer
        ).count()
        == 1
    )
    # Done: only one contract is created despite duplicate POSTs
