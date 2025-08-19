import csv
import io
import uuid
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from nadooit_crm.models import Customer
from nadooit_hr.models import Employee
from nadooit_program.models import Program
from nadooit_time_account.models import TimeAccount
from nadooit_program_ownership_system.models import CustomerProgram
from nadooit_api_executions_system.models import CustomerProgramExecution


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(
        username="csvuser", email="csv@example.com", password="pw", is_active=True
    )


@pytest.fixture
def employee(db, user):
    return Employee.objects.create(user=user)


@pytest.fixture
def customer(db):
    return Customer.objects.create(name="Acme Corp")


@pytest.fixture
def time_account(db):
    return TimeAccount.objects.create(time_balance_in_seconds=0)


@pytest.fixture
def program(db):
    return Program.objects.create(name="Std Program")


@pytest.fixture
def customer_program(db, customer, program, time_account):
    return CustomerProgram.objects.create(
        customer=customer,
        program=program,
        time_account=time_account,
        program_time_saved_per_execution_in_seconds=30,
    )


def _reverse_export(customer_id, filter_type="last20"):
    return reverse(
        "nadooit_os:export-transactions",
        kwargs={"filter_type": filter_type, "cutomer_id": customer_id},
    )


def _parse_csv(response):
    content = response.content.decode("utf-8")
    return list(csv.reader(io.StringIO(content)))


def test_export_transactions_requires_login(db, client, customer):
    url = _reverse_export(customer.id)
    resp = client.get(url)
    assert resp.status_code in (301, 302)
    assert "login-user" in resp.url


def test_export_transactions_customer_not_found(db, client, user, employee):
    client.force_login(user)
    bogus = uuid.uuid4()
    url = _reverse_export(bogus)
    resp = client.get(url)
    assert resp.status_code == 404
    assert b"Customer not found" in resp.content


def test_export_transactions_unknown_filter_header_only(
    db, client, user, employee, customer
):
    client.force_login(user)
    url = _reverse_export(customer.id, filter_type="unknown")
    resp = client.get(url)
    assert resp.status_code == 200
    assert resp["Content-Type"] == "text/csv"
    assert resp["Content-Disposition"].startswith("attachment; filename=")
    rows = _parse_csv(resp)
    # Only header row expected
    assert rows[0] == ["id", "Programmname", "erspaarte Zeit", "Preis", "Erstellt"]
    assert len(rows) == 1


@pytest.mark.parametrize(
    "prog_name, expected_prefix",
    [
        ("=SUM(1,1)", "''"),  # direct risky
        (" +CMD", "'"),  # space before risky
        ("\t@IMP", "''"),  # non-space whitespace before risky
    ],
)
def test_export_transactions_sanitizes_formula_injection(
    db,
    client,
    user,
    employee,
    customer,
    time_account,
    prog_name,
    expected_prefix,
):
    client.force_login(user)

    program = Program.objects.create(name=prog_name)
    cp = CustomerProgram.objects.create(
        customer=customer,
        program=program,
        time_account=time_account,
        program_time_saved_per_execution_in_seconds=42,
    )
    CustomerProgramExecution.objects.create(
        customer_program=cp,
        program_time_saved_in_seconds=42,
        payment_status=CustomerProgramExecution.PaymentStatus.NOT_PAID,
        price_for_execution=0,
    )

    url = _reverse_export(customer.id, filter_type="last20")
    resp = client.get(url)
    assert resp.status_code == 200
    rows = _parse_csv(resp)
    assert len(rows) == 2  # header + one row
    header, data = rows
    assert header == ["id", "Programmname", "erspaarte Zeit", "Preis", "Erstellt"]
    # Column order: id, Programmname, erspaarte Zeit, Preis, Erstellt
    prog_cell = data[1]
    assert prog_cell.startswith(expected_prefix)
    # The risky content still present after prefixing
    assert prog_cell.endswith(prog_name)
