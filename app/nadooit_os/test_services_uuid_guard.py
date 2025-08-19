import pytest
from model_bakery import baker

from nadooit_os import services


def test_customer_id_checks_handle_malformed(db):
    assert (
        services.check__customer__exists__for__customer_id("1 OR 1=1")
        is False
    )
    assert (
        services.get__customer__for__customer_id("1 OR 1=1")
        is None
    )


def test_customer_id_checks_valid(db):
    customer = baker.make("nadooit_crm.Customer")
    assert services.check__customer__exists__for__customer_id(customer.id) is True
    assert services.get__customer__for__customer_id(customer.id) == customer


def test_cpe_id_checks_handle_malformed(db):
    assert (
        services.check__customer_program_execution__exists__for__customer_program_execution_id(
            "bad"
        )
        is False
    )
    assert (
        services.get__customer_program_execution__for__customer_program_execution_id(
            "bad"
        )
        is None
    )


def test_cpe_id_checks_valid(db):
    cpe = baker.make("nadooit_api_executions_system.CustomerProgramExecution")
    assert (
        services.check__customer_program_execution__exists__for__customer_program_execution_id(
            cpe.id
        )
        is True
    )
    assert (
        services.get__customer_program_execution__for__customer_program_execution_id(
            cpe.id
        )
        == cpe
    )
