import io
import csv
import uuid
import pytest
from model_bakery import baker
from django.urls import reverse

from nadooit_os.services import (
    get__customer__for__customer_id,
    check__customer__exists__for__customer_id,
    get__customer_program_execution__for__customer_program_execution_id,
    get__csv__for__list_of_customer_program_executions,
    get__customer_program_executions__for__filter_type_and_customer,
    get__not_paid_customer_program_executions__for__filter_type_and_customer,
    get__employee__for__employee_id,
    get__customer_program__for__customer_program_id,
    get__employee_contract__for__employee_contract_id,
)


@pytest.mark.django_db
def test_id_based_lookups_resist_sql_injection_like_inputs():
    # Create some baseline data to ensure the DB isn't empty
    baker.make("nadooit_crm.Customer")
    baker.make("nadooit_api_executions_system.CustomerProgramExecution")

    injection_like = "1 OR 1=1"

    # Functions should not error and should not return unintended results
    assert check__customer__exists__for__customer_id(injection_like) is False
    assert get__customer__for__customer_id(injection_like) is None
    assert (
        get__customer_program_execution__for__customer_program_execution_id(
            injection_like
        )
        is None
    )


@pytest.mark.django_db
def test_csv_export_escapes_spreadsheet_formulas():
    # Create data where a text field begins with '=' which many spreadsheet tools treat as a formula
    program = baker.make("nadooit_program.Program", name='=HYPERLINK("http://evil","cmd")')
    customer = baker.make("nadooit_crm.Customer")
    customer_program = baker.make(
        "nadooit_program_ownership_system.CustomerProgram", customer=customer, program=program
    )
    cpe = baker.make(
        "nadooit_api_executions_system.CustomerProgramExecution",
        customer_program=customer_program,
        program_time_saved_in_seconds=30,
        price_for_execution=10,
    )

    response = get__csv__for__list_of_customer_program_executions([cpe])
    assert response["Content-Type"] == "text/csv"
    content = response.content.decode("utf-8")

    rows = list(csv.reader(io.StringIO(content)))
    # header + one data row expected
    assert len(rows) >= 2

    program_name_cell = rows[1][1]
    # Expect mitigation (e.g., prefix with a single quote) so the first character is not one of = + - @
    assert program_name_cell and program_name_cell[0] not in {"=", "+", "-", "@"}
    # Our sanitizer prefixes a single quote
    assert program_name_cell.startswith("'")


@pytest.mark.django_db
def test_get_customer_program_executions_handles_unrecognized_filter_type_safely():
    # Setup minimal data
    customer = baker.make("nadooit_crm.Customer")
    # Unrecognized filter type should not crash and should return None or a queryset
    unsafe_filter = "last20; DROP TABLE x;"  # representative junk
    result = get__customer_program_executions__for__filter_type_and_customer(
        unsafe_filter, customer
    )
    # Accept either None (current implementation) or a QuerySet-like (future hardening)
    assert result is None or hasattr(result, "filter")


@pytest.mark.django_db
def test_csv_export_sanitizes_leading_whitespace_then_formula():
    # Program name starts with spaces before a formula marker
    program = baker.make("nadooit_program.Program", name='   =1+1')
    customer = baker.make("nadooit_crm.Customer")
    customer_program = baker.make(
        "nadooit_program_ownership_system.CustomerProgram", customer=customer, program=program
    )
    cpe = baker.make(
        "nadooit_api_executions_system.CustomerProgramExecution",
        customer_program=customer_program,
        program_time_saved_in_seconds=1,
        price_for_execution=1,
    )

    response = get__csv__for__list_of_customer_program_executions([cpe])
    content = response.content.decode("utf-8")
    rows = list(csv.reader(io.StringIO(content)))
    assert len(rows) >= 2
    program_name_cell = rows[1][1]
    assert program_name_cell.startswith("'")
    # After stripping the added quote, still begins with spaces then '='
    assert program_name_cell[1:].startswith("   =")


@pytest.mark.django_db
def test_csv_export_benign_text_not_modified():
    benign_name = "Hello World"
    program = baker.make("nadooit_program.Program", name=benign_name)
    customer = baker.make("nadooit_crm.Customer")
    customer_program = baker.make(
        "nadooit_program_ownership_system.CustomerProgram", customer=customer, program=program
    )
    cpe = baker.make(
        "nadooit_api_executions_system.CustomerProgramExecution",
        customer_program=customer_program,
        program_time_saved_in_seconds=1,
        price_for_execution=1,
    )

    response = get__csv__for__list_of_customer_program_executions([cpe])
    content = response.content.decode("utf-8")
    rows = list(csv.reader(io.StringIO(content)))
    assert len(rows) >= 2
    program_name_cell = rows[1][1]
    assert program_name_cell == benign_name


@pytest.mark.django_db
def test_csv_export_sanitizes_various_formula_prefixes():
    # Verify that +, -, @, and whitespace+formula are all neutralized
    prefixes = ["+SUM(1,1)", "-1", "@A1", "\t+2", "\n-3", "\r=@X"]
    cpes = []
    customer = baker.make("nadooit_crm.Customer")
    for i, name in enumerate(prefixes):
        program = baker.make("nadooit_program.Program", name=name)
        customer_program = baker.make(
            "nadooit_program_ownership_system.CustomerProgram",
            customer=customer,
            program=program,
        )
        cpe = baker.make(
            "nadooit_api_executions_system.CustomerProgramExecution",
            customer_program=customer_program,
            program_time_saved_in_seconds=1 + i,
            price_for_execution=1 + i,
        )
        cpes.append(cpe)

    response = get__csv__for__list_of_customer_program_executions(cpes)
    content = response.content.decode("utf-8")
    rows = list(csv.reader(io.StringIO(content)))
    # header + len(prefixes) rows expected
    assert len(rows) == 1 + len(prefixes)
    # Program name is the second column
    for idx, name in enumerate(prefixes, start=1):
        program_name_cell = rows[idx][1]
        assert program_name_cell.startswith("'")
        # ensure not starting with risky chars after sanitization
        assert program_name_cell[1:].lstrip()[:1] not in {"=", "+", "-", "@"}


@pytest.mark.django_db
def test_csv_export_leading_single_quote_remains_unchanged():
    # A value that already starts safe with a quote should not get another one
    original = "'Already safe"
    program = baker.make("nadooit_program.Program", name=original)
    customer = baker.make("nadooit_crm.Customer")
    customer_program = baker.make(
        "nadooit_program_ownership_system.CustomerProgram", customer=customer, program=program
    )
    cpe = baker.make(
        "nadooit_api_executions_system.CustomerProgramExecution",
        customer_program=customer_program,
        program_time_saved_in_seconds=1,
        price_for_execution=1,
    )

    response = get__csv__for__list_of_customer_program_executions([cpe])
    content = response.content.decode("utf-8")
    rows = list(csv.reader(io.StringIO(content)))
    assert rows[1][1] == original


@pytest.mark.django_db
def test_get_not_paid_wrapper_unknown_filter_returns_empty_queryset():
    customer = baker.make("nadooit_crm.Customer")
    # Even if there are NOT_PAID executions, unknown filter should lead to empty queryset
    customer_program = baker.make(
        "nadooit_program_ownership_system.CustomerProgram", customer=customer
    )
    baker.make(
        "nadooit_api_executions_system.CustomerProgramExecution",
        customer_program=customer_program,
        payment_status="NOT_PAID",
    )

    qs = get__not_paid_customer_program_executions__for__filter_type_and_customer(
        "unknown_filter", customer
    )
    # Should be a queryset-like and empty
    assert hasattr(qs, "count")
    assert qs.count() == 0


@pytest.mark.django_db
def test_more_id_based_helpers_resist_sql_injection_like_inputs():
    # Ensure additional helpers do not error and return no unintended objects
    baker.make("nadooit_hr.Employee")
    baker.make("nadooit_program_ownership_system.CustomerProgram")
    baker.make("nadooit_hr.EmployeeContract")

    injection_like = "1 OR 1=1"
    assert get__employee__for__employee_id(injection_like) is None
    assert get__customer_program__for__customer_program_id(injection_like) is None
    assert get__employee_contract__for__employee_contract_id(injection_like) is None


@pytest.mark.django_db
def test_export_transactions_unknown_filter_returns_header_only_csv(client):
    # Auth required
    user = baker.make("nadooit_auth.User")
    client.force_login(user)
    customer = baker.make("nadooit_crm.Customer")

    url = reverse(
        "nadooit_os:export-transactions", args=["unknown_filter", customer.id]
    )
    resp = client.get(url)
    assert resp.status_code == 200
    assert resp["Content-Type"] == "text/csv"
    assert resp["Content-Disposition"].startswith("attachment; filename=")

    rows = list(csv.reader(io.StringIO(resp.content.decode("utf-8"))))
    # Expect only header row
    assert len(rows) == 1


@pytest.mark.django_db
def test_export_transactions_customer_not_found_returns_404(client):
    user = baker.make("nadooit_auth.User")
    client.force_login(user)
    non_existent_customer_id = uuid.uuid4()

    url = reverse(
        "nadooit_os:export-transactions", args=["last20", non_existent_customer_id]
    )
    resp = client.get(url)
    assert resp.status_code == 404


@pytest.mark.django_db
def test_export_transactions_sanitizes_program_name_in_csv(client):
    user = baker.make("nadooit_auth.User")
    client.force_login(user)
    customer = baker.make("nadooit_crm.Customer")
    program = baker.make(
        "nadooit_program.Program", name='=HYPERLINK("http://evil","cmd")'
    )
    customer_program = baker.make(
        "nadooit_program_ownership_system.CustomerProgram",
        customer=customer,
        program=program,
    )
    baker.make(
        "nadooit_api_executions_system.CustomerProgramExecution",
        customer_program=customer_program,
        payment_status="NOT_PAID",
    )

    url = reverse("nadooit_os:export-transactions", args=["last20", customer.id])
    resp = client.get(url)
    assert resp.status_code == 200
    rows = list(csv.reader(io.StringIO(resp.content.decode("utf-8"))))
    assert len(rows) >= 2
    assert rows[1][1].startswith("'")


@pytest.mark.django_db
def test_grouped_by_customer_resilient_to_unknown_filter_type():
    from nadooit_os.services import (
        get__list_of_customer_program_execution__for__employee_and_filter_type__grouped_by_customer,
    )

    employee = baker.make("nadooit_hr.Employee")
    # With no contracts, should just return empty list regardless of filter
    result = get__list_of_customer_program_execution__for__employee_and_filter_type__grouped_by_customer(
        employee, filter_type="unknown; DROP"
    )
    assert isinstance(result, list)
    assert result == []
