import pytest
from django.urls import reverse
from model_bakery import baker

from nadooit_hr.models import (
    EmployeeContract,
    TimeAccountManagerContract,
    CustomerProgramExecutionManagerContract,
    CustomerProgramManagerContract,
)


@pytest.mark.django_db
class TestTimeAccountRoleGiving:
    def test_denied_for_other_customer(self, client):
        customer_a = baker.make("nadooit_crm.Customer")
        customer_b = baker.make("nadooit_crm.Customer")

        manager_user = baker.make("nadooit_auth.User")
        manager_employee = baker.make("nadooit_hr.Employee", user=manager_user)
        # Manager has contract and can_give_manager_role for customer A only
        manager_contract_a = baker.make(
            EmployeeContract,
            employee=manager_employee,
            customer=customer_a,
            is_active=True,
        )
        baker.make(
            TimeAccountManagerContract,
            contract=manager_contract_a,
            can_give_manager_role=True,
            # also give create to ensure ability grant path would be allowed if authorized
            can_create_time_accounts=True,
        )

        target_user = baker.make("nadooit_auth.User")

        client.force_login(manager_user)
        url = reverse("nadooit_os:give-customer-time-account-manager-role")
        resp = client.post(
            url,
            {
                "user_code": target_user.user_code,
                "customers": str(customer_b.id),
                "role": ["can_create_time_accounts"],
            },
        )

        assert resp.status_code == 403


@pytest.mark.django_db
class TestRoleGivingNoImplicitCreation:
    def test_time_account_view_does_not_create_acting_manager_contract(self, client):
        customer = baker.make("nadooit_crm.Customer")

        # Acting user has an EmployeeContract but no TACM manager contract
        acting_user = baker.make("nadooit_auth.User")
        acting_employee = baker.make("nadooit_hr.Employee", user=acting_user)
        baker.make(
            EmployeeContract,
            employee=acting_employee,
            customer=customer,
            is_active=True,
        )
        target_user = baker.make("nadooit_auth.User")

        client.force_login(acting_user)
        url = reverse("nadooit_os:give-customer-time-account-manager-role")
        resp = client.post(
            url,
            {
                "user_code": target_user.user_code,
                "customers": str(customer.id),
                "role": ["can_create_time_accounts"],
            },
        )

        assert resp.status_code == 403
        # Ensure no TACM manager contract was implicitly created for the acting user
        assert (
            TimeAccountManagerContract.objects.filter(
                contract__employee__user=acting_user, contract__customer=customer
            ).count()
            == 0
        )

    def test_cpem_view_does_not_create_acting_manager_contract(self, client):
        customer = baker.make("nadooit_crm.Customer")

        acting_user = baker.make("nadooit_auth.User")
        acting_employee = baker.make("nadooit_hr.Employee", user=acting_user)
        baker.make(
            EmployeeContract,
            employee=acting_employee,
            customer=customer,
            is_active=True,
        )
        target_user = baker.make("nadooit_auth.User")

        client.force_login(acting_user)
        url = reverse("nadooit_os:give-customer-program-execution-manager-role")
        resp = client.post(
            url,
            {
                "user_code": target_user.user_code,
                "customer_id": str(customer.id),
                "role": ["can_create_customer_program_execution"],
            },
        )

        assert resp.status_code == 403
        assert (
            CustomerProgramExecutionManagerContract.objects.filter(
                contract__employee__user=acting_user, contract__customer=customer
            ).count()
            == 0
        )

    def test_cpm_view_does_not_create_acting_manager_contract(self, client):
        customer = baker.make("nadooit_crm.Customer")

        acting_user = baker.make("nadooit_auth.User")
        acting_employee = baker.make("nadooit_hr.Employee", user=acting_user)
        baker.make(
            EmployeeContract,
            employee=acting_employee,
            customer=customer,
            is_active=True,
        )
        target_user = baker.make("nadooit_auth.User")

        client.force_login(acting_user)
        url = reverse("nadooit_os:give-customer-program-manager-role")
        resp = client.post(
            url,
            {
                "user_code": target_user.user_code,
                "customers": str(customer.id),
                "role": ["can_create_customer_program"],
            },
        )

        assert resp.status_code == 403
        assert (
            CustomerProgramManagerContract.objects.filter(
                contract__employee__user=acting_user, contract__customer=customer
            ).count()
            == 0
        )

    def test_allowed_same_customer(self, client):
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
            TimeAccountManagerContract,
            contract=manager_contract,
            can_give_manager_role=True,
            can_create_time_accounts=True,
        )

        target_user = baker.make("nadooit_auth.User")

        client.force_login(manager_user)
        url = reverse("nadooit_os:give-customer-time-account-manager-role")
        resp = client.post(
            url,
            {
                "user_code": target_user.user_code,
                "customers": str(customer.id),
                "role": ["can_create_time_accounts"],
            },
        )

        assert resp.status_code in (200, 302)
        assert TimeAccountManagerContract.objects.filter(
            contract__employee__user=target_user,
            contract__customer=customer,
        ).exists()


@pytest.mark.django_db
class TestCustomerProgramExecutionRoleGiving:
    def test_denied_for_other_customer(self, client):
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
            CustomerProgramExecutionManagerContract,
            contract=manager_contract_a,
            can_give_manager_role=True,
            can_create_customer_program_execution=True,
        )

        target_user = baker.make("nadooit_auth.User")

        client.force_login(manager_user)
        url = reverse("nadooit_os:give-customer-program-execution-manager-role")
        resp = client.post(
            url,
            {
                "user_code": target_user.user_code,
                "customer_id": str(customer_b.id),
                "role": ["can_create_customer_program_execution"],
            },
        )

        assert resp.status_code == 403
        assert not CustomerProgramExecutionManagerContract.objects.filter(
            contract__employee__user=target_user,
            contract__customer=customer_b,
        ).exists()

    def test_allowed_same_customer(self, client):
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
            CustomerProgramExecutionManagerContract,
            contract=manager_contract,
            can_give_manager_role=True,
            can_create_customer_program_execution=True,
        )

        target_user = baker.make("nadooit_auth.User")

        client.force_login(manager_user)
        url = reverse("nadooit_os:give-customer-program-execution-manager-role")
        resp = client.post(
            url,
            {
                "user_code": target_user.user_code,
                "customer_id": str(customer.id),
                "role": ["can_create_customer_program_execution"],
            },
        )

        assert resp.status_code in (200, 302)
        assert CustomerProgramExecutionManagerContract.objects.filter(
            contract__employee__user=target_user,
            contract__customer=customer,
        ).exists()


@pytest.mark.django_db
class TestCustomerProgramManagerRoleGiving:
    def test_denied_for_other_customer(self, client):
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
            CustomerProgramManagerContract,
            contract=manager_contract_a,
            can_give_manager_role=True,
            can_create_customer_program=True,
        )

        target_user = baker.make("nadooit_auth.User")

        client.force_login(manager_user)
        url = reverse("nadooit_os:give-customer-program-manager-role")
        resp = client.post(
            url,
            {
                "user_code": target_user.user_code,
                "customers": str(customer_b.id),
                "role": ["can_create_customer_program"],
            },
        )

        assert resp.status_code == 403
        assert not CustomerProgramManagerContract.objects.filter(
            contract__employee__user=target_user,
            contract__customer=customer_b,
        ).exists()

    def test_allowed_same_customer(self, client):
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
            CustomerProgramManagerContract,
            contract=manager_contract,
            can_give_manager_role=True,
            can_create_customer_program=True,
        )

        target_user = baker.make("nadooit_auth.User")

        client.force_login(manager_user)
        url = reverse("nadooit_os:give-customer-program-manager-role")
        resp = client.post(
            url,
            {
                "user_code": target_user.user_code,
                "customers": str(customer.id),
                "role": ["can_create_customer_program"],
            },
        )

        assert resp.status_code in (200, 302)
        assert CustomerProgramManagerContract.objects.filter(
            contract__employee__user=target_user,
            contract__customer=customer,
        ).exists()


@pytest.mark.django_db
class TestRoleGivingIdempotency:
    def test_time_account_role_giving_idempotent(self, client):
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
            TimeAccountManagerContract,
            contract=manager_contract,
            can_give_manager_role=True,
            can_create_time_accounts=True,
        )

        target_user = baker.make("nadooit_auth.User")

        client.force_login(manager_user)
        url = reverse("nadooit_os:give-customer-time-account-manager-role")
        payload = {
            "user_code": target_user.user_code,
            "customers": str(customer.id),
            "role": ["can_create_time_accounts"],
        }

        # Double POST
        resp1 = client.post(url, payload)
        resp2 = client.post(url, payload)

        assert resp1.status_code in (200, 302)
        assert resp2.status_code in (200, 302)
        assert (
            TimeAccountManagerContract.objects.filter(
                contract__employee__user=target_user, contract__customer=customer
            ).count()
            == 1
        )

    def test_customer_program_execution_role_giving_idempotent(self, client):
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
            CustomerProgramExecutionManagerContract,
            contract=manager_contract,
            can_give_manager_role=True,
            can_create_customer_program_execution=True,
        )

        target_user = baker.make("nadooit_auth.User")

        client.force_login(manager_user)
        url = reverse("nadooit_os:give-customer-program-execution-manager-role")
        payload = {
            "user_code": target_user.user_code,
            "customer_id": str(customer.id),
            "role": ["can_create_customer_program_execution"],
        }

        # Double POST
        resp1 = client.post(url, payload)
        resp2 = client.post(url, payload)

        assert resp1.status_code in (200, 302)
        assert resp2.status_code in (200, 302)
        assert (
            CustomerProgramExecutionManagerContract.objects.filter(
                contract__employee__user=target_user, contract__customer=customer
            ).count()
            == 1
        )

    def test_customer_program_manager_role_giving_idempotent(self, client):
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
            CustomerProgramManagerContract,
            contract=manager_contract,
            can_give_manager_role=True,
            can_create_customer_program=True,
        )

        target_user = baker.make("nadooit_auth.User")

        client.force_login(manager_user)
        url = reverse("nadooit_os:give-customer-program-manager-role")
        payload = {
            "user_code": target_user.user_code,
            "customers": str(customer.id),
            "role": ["can_create_customer_program"],
        }

        # Double POST
        resp1 = client.post(url, payload)
        resp2 = client.post(url, payload)

        assert resp1.status_code in (200, 302)
        assert resp2.status_code in (200, 302)
        assert (
            CustomerProgramManagerContract.objects.filter(
                contract__employee__user=target_user, contract__customer=customer
            ).count()
            == 1
        )


@pytest.mark.django_db
class TestRoleGivingMissingAbility:
    def test_time_account_role_giving_denied_without_can_give(self, client):
        customer = baker.make("nadooit_crm.Customer")

        manager_user = baker.make("nadooit_auth.User")
        manager_employee = baker.make("nadooit_hr.Employee", user=manager_user)
        manager_contract = baker.make(
            EmployeeContract,
            employee=manager_employee,
            customer=customer,
            is_active=True,
        )
        # Manager lacks can_give_manager_role
        baker.make(
            TimeAccountManagerContract,
            contract=manager_contract,
            can_give_manager_role=False,
            can_create_time_accounts=True,
        )

        target_user = baker.make("nadooit_auth.User")

        client.force_login(manager_user)
        url = reverse("nadooit_os:give-customer-time-account-manager-role")
        resp = client.post(
            url,
            {
                "user_code": target_user.user_code,
                "customers": str(customer.id),
                "role": ["can_create_time_accounts"],
            },
        )
        assert resp.status_code == 403

    def test_customer_program_execution_role_giving_denied_without_can_give(self, client):
        customer = baker.make("nadooit_crm.Customer")

        manager_user = baker.make("nadooit_auth.User")
        manager_employee = baker.make("nadooit_hr.Employee", user=manager_user)
        manager_contract = baker.make(
            EmployeeContract,
            employee=manager_employee,
            customer=customer,
            is_active=True,
        )
        # Manager lacks can_give_manager_role
        baker.make(
            CustomerProgramExecutionManagerContract,
            contract=manager_contract,
            can_give_manager_role=False,
            can_create_customer_program_execution=True,
        )

        target_user = baker.make("nadooit_auth.User")

        client.force_login(manager_user)
        url = reverse("nadooit_os:give-customer-program-execution-manager-role")
        resp = client.post(
            url,
            {
                "user_code": target_user.user_code,
                "customer_id": str(customer.id),
                "role": ["can_create_customer_program_execution"],
            },
        )
        assert resp.status_code == 403

    def test_customer_program_manager_role_giving_denied_without_can_give(self, client):
        customer = baker.make("nadooit_crm.Customer")

        manager_user = baker.make("nadooit_auth.User")
        manager_employee = baker.make("nadooit_hr.Employee", user=manager_user)
        manager_contract = baker.make(
            EmployeeContract,
            employee=manager_employee,
            customer=customer,
            is_active=True,
        )
        # Manager lacks can_give_manager_role
        baker.make(
            CustomerProgramManagerContract,
            contract=manager_contract,
            can_give_manager_role=False,
            can_create_customer_program=True,
        )

        target_user = baker.make("nadooit_auth.User")

        client.force_login(manager_user)
        url = reverse("nadooit_os:give-customer-program-manager-role")
        resp = client.post(
            url,
            {
                "user_code": target_user.user_code,
                "customers": str(customer.id),
                "role": ["can_create_customer_program"],
            },
        )
        assert resp.status_code == 403
