import pytest
import rest_framework.response
from django.test import Client
from django.urls import reverse
from model_bakery import baker
from nadooit_api_key.models import NadooitApiKey
from nadooit_os.services import create__NadooitApiKey__for__user
from nadooit_auth.models import User
from nadooit_crm.models import Customer
from nadooit_hr.models import CustomerProgramManagerContract, Employee, EmployeeContract
from nadooit_program.models import Program
from nadooit_program_ownership_system.models import CustomerProgram
from nadooit_time_account.models import TimeAccount


@pytest.mark.django_db
def test_create_execution():
    # create a user
    user = baker.make(User)

    baker.make(Employee, user=user)

    customer = baker.make(Customer)

    EmployeeContract.objects.create(
        employee=user.employee,
        customer=customer,
    )

    customer_program = baker.make(
        CustomerProgram,
        customer=customer,
        program=baker.make(Program, name="test"),
        time_account=baker.make(TimeAccount, time_balance_in_seconds=0),
    )

    # Create API key via service to get a known raw value
    import uuid
    raw_key = uuid.uuid4()
    Nadooit_api_key = create__NadooitApiKey__for__user(user, raw_key)

    client = Client()

    respone = client.post(
        reverse("create-execution"),
        data={
            "program_id": customer_program.id,
            "NADOOIT__USER_CODE": user.user_code,
            "NADOOIT__API_KEY": str(raw_key),
        },
    )

    assert respone.status_code == 200


@pytest.mark.django_db
def test_create_execution__with__invalid__user_code():
    # create a user
    user = baker.make(User)

    baker.make(Employee, user=user)

    customer = baker.make(Customer)

    EmployeeContract.objects.create(
        employee=user.employee,
        customer=customer,
    )

    customer_program = baker.make(
        CustomerProgram,
        customer=customer,
        program=baker.make(Program, name="test"),
        time_account=baker.make(TimeAccount, time_balance_in_seconds=0),
    )

    # Create API key via service to get a known raw value
    import uuid
    raw_key = uuid.uuid4()
    create__NadooitApiKey__for__user(user, raw_key)

    client = Client()

    respone = client.post(
        reverse("create-execution"),
        data={
            "program_id": customer_program.id,
            "NADOOIT__USER_CODE": "invalid user code",
            "NADOOIT__API_KEY": str(raw_key),
        },
    )

    assert respone.status_code == 403


@pytest.mark.django_db
def test_create_execution__with__invalid__api_key():
    # create a user
    user = baker.make(User)

    baker.make(Employee, user=user)

    customer = baker.make(Customer)

    EmployeeContract.objects.create(
        employee=user.employee,
        customer=customer,
    )

    customer_program = baker.make(
        CustomerProgram,
        customer=customer,
        program=baker.make(Program, name="test"),
        time_account=baker.make(TimeAccount, time_balance_in_seconds=0),
    )

    client = Client()

    respone = client.post(
        reverse("create-execution"),
        data={
            "program_id": customer_program.id,
            "NADOOIT__USER_CODE": user.user_code,
            "NADOOIT__API_KEY": "invalid api key",
        },
    )

    assert respone.status_code == 403


@pytest.mark.django_db
def test_check_user():
    # create a user
    user = baker.make(User, user_code="nadoo01")

    baker.make(Employee, user=user)

    customer = baker.make(Customer)

    EmployeeContract.objects.create(
        employee=user.employee,
        customer=customer,
    )

    # Create API key via service to get a known raw value
    import uuid
    raw_key = uuid.uuid4()
    create__NadooitApiKey__for__user(user, raw_key)

    client = Client()

    respone = client.post(
        reverse("check"),
        data={
            "NADOOIT__USER_CODE": user.user_code,
            "NADOOIT__USER_CODE_TO_CHECK": user.user_code,
            "NADOOIT__API_KEY": str(raw_key),
        },
    )

    assert respone.status_code == 200
