import pytest
from django.test import RequestFactory
from django.template import loader


@pytest.mark.django_db
def test_time_account_template_escapes_error_xss():
    template = loader.get_template(
        "nadooit_os/time_account/give_customer_time_account_manager_role.html"
    )
    rf = RequestFactory()
    request = rf.get("/nadooit-os/time-account/give-customer-time-account-manager-role")

    payload = "<script>alert(1)</script>"
    html = template.render({"error": payload}, request)

    assert payload not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html


@pytest.mark.django_db
def test_customer_program_exec_template_escapes_error_xss():
    template = loader.get_template(
        "nadooit_os/customer_program_execution/give_customer_program_execution_manager_role.html"
    )
    rf = RequestFactory()
    request = rf.get(
        "/nadooit-os/customer-program-execution/give-customer-program-execution-manager-role"
    )

    payload = "<img src=x onerror=alert(1)>"
    html = template.render({"error": payload}, request)

    assert "<img" not in html
    assert "&lt;img src=x onerror=alert(1)&gt;" in html


@pytest.mark.django_db
def test_hr_add_employee_template_escapes_error_xss():
    template = loader.get_template("nadooit_os/hr_department/add_employee.html")
    rf = RequestFactory()
    request = rf.get("/nadooit-os/hr/add-employee")

    payload = "<b onclick=alert(1)>bold</b>"
    html = template.render({"error": payload}, request)

    assert "<b" not in html
    assert "&lt;b onclick=alert(1)&gt;bold&lt;/b&gt;" in html
