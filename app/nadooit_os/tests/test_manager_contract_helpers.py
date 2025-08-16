import pytest
from model_bakery import baker

from nadooit_hr.models import (
    Employee,
    EmployeeContract,
    TimeAccountManagerContract,
    CustomerProgramExecutionManagerContract,
    CustomerProgramManagerContract,
)
from nadooit_crm.models import Customer

from nadooit_os.services import (
    create__time_account_manager_contract__for__employee_and_customer,
    set__list_of_abilities__for__time_account_manager_contract_according_to_list_of_abilities,
    get_only__time_account_manager_contract__for__employee_and_customer,
    create__customer_program_execution_manager_contract__for__employee_and_customer,
    create__customer_program_execution_manager_contract__for__employee_contract,
    set__list_of_abilities__for__customer_program_execution_manager_contract_according_to_list_of_abilities,
    get_only__customer_program_execution_manager_contract__for__employee_and_customer,
    create__customer_program_manager_contract__for__employee_and__customer,
    get_only__customer_program_manager_contract__for__employee_and_customer,
    set__list_of_abilities__for__customer_program_manager_contract_according_to_list_of_abilities,
)


@pytest.mark.django_db
def test_create_TACM_reuses_employee_contract_and_does_not_duplicate_employee_contracts():
    customer = baker.make("nadooit_crm.Customer")
    employee = baker.make("nadooit_hr.Employee", user=baker.make("nadooit_auth.User"))

    # precondition: no EmployeeContract exists
    assert (
        EmployeeContract.objects.filter(employee=employee, customer=customer).count()
        == 0
    )

    # Act: call create twice
    tacm1 = create__time_account_manager_contract__for__employee_and_customer(
        employee, customer
    )
    tacm2 = create__time_account_manager_contract__for__employee_and_customer(
        employee, customer
    )

    # Assert: exactly one EmployeeContract was created and reused
    assert tacm1.contract == tacm2.contract
    assert (
        EmployeeContract.objects.filter(employee=employee, customer=customer).count()
        == 1
    )


@pytest.mark.django_db
def test_create_CPEM_for_employee_and_customer_reuses_employee_contract():
    customer = baker.make("nadooit_crm.Customer")
    employee = baker.make("nadooit_hr.Employee", user=baker.make("nadooit_auth.User"))

    assert (
        EmployeeContract.objects.filter(employee=employee, customer=customer).count()
        == 0
    )

    cpem1 = create__customer_program_execution_manager_contract__for__employee_and_customer(
        employee, customer
    )
    cpem2 = create__customer_program_execution_manager_contract__for__employee_and_customer(
        employee, customer
    )

    assert cpem1.contract == cpem2.contract
    assert (
        EmployeeContract.objects.filter(employee=employee, customer=customer).count()
        == 1
    )


@pytest.mark.django_db
def test_create_CPEM_for_employee_contract_is_idempotent():
    # Given an EmployeeContract
    employee = baker.make("nadooit_hr.Employee", user=baker.make("nadooit_auth.User"))
    customer = baker.make("nadooit_crm.Customer")
    employee_contract = baker.make(
        "nadooit_hr.EmployeeContract", employee=employee, customer=customer
    )

    # When creating a CPE Manager contract twice for the same employee_contract
    c1 = create__customer_program_execution_manager_contract__for__employee_contract(
        employee_contract
    )
    c2 = create__customer_program_execution_manager_contract__for__employee_contract(
        employee_contract
    )

    # Then only one CPE Manager contract exists
    assert c1 == c2
    assert (
        CustomerProgramExecutionManagerContract.objects.filter(
            contract=employee_contract
        ).count()
        == 1
    )


@pytest.mark.django_db
def test_TACM_setter_idempotent_unknown_ignored_and_gated():
    customer = baker.make("nadooit_crm.Customer")

    # Creator with TACM on same customer and abilities
    creator = baker.make("nadooit_hr.Employee", user=baker.make("nadooit_auth.User"))
    creator_contract = baker.make(
        "nadooit_hr.EmployeeContract", employee=creator, customer=customer
    )
    baker.make(
        "nadooit_hr.TimeAccountManagerContract",
        contract=creator_contract,
        can_create_time_accounts=True,
        can_delete_time_accounts=True,
    )

    # Target employee with new TACM to set abilities on
    target = baker.make("nadooit_hr.Employee", user=baker.make("nadooit_auth.User"))
    target_contract = baker.make(
        "nadooit_hr.EmployeeContract", employee=target, customer=customer
    )
    target_tacm = baker.make(
        "nadooit_hr.TimeAccountManagerContract", contract=target_contract
    )

    # Act: set abilities twice including an unknown ability
    abilities = [
        "can_create_time_accounts",
        "can_delete_time_accounts",
        "totally_unknown_ability",
    ]
    set__list_of_abilities__for__time_account_manager_contract_according_to_list_of_abilities(
        target_tacm, abilities, creator
    )
    set__list_of_abilities__for__time_account_manager_contract_according_to_list_of_abilities(
        target_tacm, abilities, creator
    )

    # Refresh from DB and assert both abilities are True; unknown did not break anything
    target_tacm_refreshed = TimeAccountManagerContract.objects.get(pk=target_tacm.pk)
    assert target_tacm_refreshed.can_create_time_accounts is True
    assert target_tacm_refreshed.can_delete_time_accounts is True


@pytest.mark.django_db
def test_CPEM_setter_idempotent_unknown_ignored_and_gated():
    customer = baker.make("nadooit_crm.Customer")

    # Creator with CPEM on same customer and abilities
    creator = baker.make("nadooit_hr.Employee", user=baker.make("nadooit_auth.User"))
    creator_contract = baker.make(
        "nadooit_hr.EmployeeContract", employee=creator, customer=customer
    )
    baker.make(
        "nadooit_hr.CustomerProgramExecutionManagerContract",
        contract=creator_contract,
        can_create_customer_program_execution=True,
        can_delete_customer_program_execution=True,
        can_give_manager_role=True,
    )

    # Target CPEM to set abilities on
    target = baker.make("nadooit_hr.Employee", user=baker.make("nadooit_auth.User"))
    target_contract = baker.make(
        "nadooit_hr.EmployeeContract", employee=target, customer=customer
    )
    target_cpem = baker.make(
        "nadooit_hr.CustomerProgramExecutionManagerContract", contract=target_contract
    )

    abilities = [
        "can_create_customer_program_execution",
        "can_delete_customer_program_execution",
        "can_give_manager_role",
        "irrelevant_ability",
    ]

    set__list_of_abilities__for__customer_program_execution_manager_contract_according_to_list_of_abilities(
        target_cpem, abilities, creator
    )
    set__list_of_abilities__for__customer_program_execution_manager_contract_according_to_list_of_abilities(
        target_cpem, abilities, creator
    )

    target_cpem_refreshed = CustomerProgramExecutionManagerContract.objects.get(
        pk=target_cpem.pk
    )
    assert target_cpem_refreshed.can_create_customer_program_execution is True
    assert target_cpem_refreshed.can_delete_customer_program_execution is True
    assert target_cpem_refreshed.can_give_manager_role is True


@pytest.mark.django_db
def test_CPMC_setter_idempotent_and_unknown_ignored():
    customer = baker.make("nadooit_crm.Customer")

    # Target CPMC to set abilities on (no gating in setter)
    employee = baker.make("nadooit_hr.Employee", user=baker.make("nadooit_auth.User"))
    cpmc = create__customer_program_manager_contract__for__employee_and__customer(
        employee, customer
    )

    abilities = [
        "can_create_customer_program",
        "can_delete_customer_program",
        "can_give_manager_role",
        "nonsense_ability",
    ]

    set__list_of_abilities__for__customer_program_manager_contract_according_to_list_of_abilities(
        cpmc, abilities
    )
    set__list_of_abilities__for__customer_program_manager_contract_according_to_list_of_abilities(
        cpmc, abilities
    )

    cpmc_refreshed = CustomerProgramManagerContract.objects.get(pk=cpmc.pk)
    assert cpmc_refreshed.can_create_customer_program is True
    assert cpmc_refreshed.can_delete_customer_program is True
    assert cpmc_refreshed.can_give_manager_role is True


@pytest.mark.django_db
@pytest.mark.parametrize(
    "getter,model_name",
    [
        (
            get_only__time_account_manager_contract__for__employee_and_customer,
            "nadooit_hr.TimeAccountManagerContract",
        ),
        (
            get_only__customer_program_execution_manager_contract__for__employee_and_customer,
            "nadooit_hr.CustomerProgramExecutionManagerContract",
        ),
        (
            get_only__customer_program_manager_contract__for__employee_and_customer,
            "nadooit_hr.CustomerProgramManagerContract",
        ),
    ],
)
def test_get_only_helpers_return_none_when_absent(getter, model_name):
    customer = baker.make("nadooit_crm.Customer")
    employee = baker.make("nadooit_hr.Employee", user=baker.make("nadooit_auth.User"))

    # Act / Assert
    assert getter(employee, customer) is None
