import uuid

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from nadooit_hr.models import Employee


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(
        username="complaintuser", email="cmp@example.com", password="pw", is_active=True
    )


@pytest.fixture
def employee(db, user):
    return Employee.objects.create(user=user)


@pytest.mark.django_db
def test_complaint_views_method_enforcement(client, user):
    # Authenticate so we hit method checks rather than login redirects
    client.force_login(user)
    # POST to GET-only view -> 405
    url_get_only = reverse(
        "nadooit_os:customer-program-execution-list-complaint-modal",
        kwargs={"customer_program_execution_id": uuid.uuid4()},
    )
    resp = client.post(url_get_only, data={})
    assert resp.status_code == 405

    # GET to POST-only view -> 405
    url_post_only = reverse(
        "nadooit_os:customer-program-execution-send-complaint",
        kwargs={"customer_program_execution_id": uuid.uuid4()},
    )
    resp = client.get(url_post_only)
    assert resp.status_code == 405


@pytest.mark.django_db
def test_complaint_modal_403_cases(client, user, employee, monkeypatch):
    client.force_login(user)

    base_kwargs = {"customer_program_execution_id": uuid.uuid4()}
    url = reverse(
        "nadooit_os:customer-program-execution-list-complaint-modal",
        kwargs=base_kwargs,
    )

    # Case 1: execution does not exist -> 403
    monkeypatch.setattr(
        "nadooit_os.views.check__customer_program_execution__exists__for__customer_program_execution_id",
        lambda _id: False,
    )
    resp = client.get(url)
    assert resp.status_code == 403

    # Case 2: execution exists but no customer -> 403
    monkeypatch.setattr(
        "nadooit_os.views.check__customer_program_execution__exists__for__customer_program_execution_id",
        lambda _id: True,
    )
    monkeypatch.setattr(
        "nadooit_os.views.get__customer__for__customer_program_execution_id",
        lambda _id: None,
    )
    resp = client.get(url)
    assert resp.status_code == 403

    # Case 3: customer present but user not manager for that customer -> 403
    class DummyCustomer:
        name = "Acme"

    monkeypatch.setattr(
        "nadooit_os.views.get__customer__for__customer_program_execution_id",
        lambda _id: DummyCustomer(),
    )
    monkeypatch.setattr(
        "nadooit_os.views.check__active_customer_program_execution_manager_contract__exists__between__employee_and_customer",
        lambda employee, customer: False,
    )
    resp = client.get(url)
    assert resp.status_code == 403


@pytest.mark.django_db
def test_send_complaint_happy_path(client, user, employee, monkeypatch):
    client.force_login(user)

    sent = {"status": False, "payment_status": None, "complainttext": None}

    # Satisfy guards
    monkeypatch.setattr(
        "nadooit_os.views.check__customer_program_execution__exists__for__customer_program_execution_id",
        lambda _id: True,
    )

    class DummyCustomer:
        name = "Acme"

    monkeypatch.setattr(
        "nadooit_os.views.get__customer__for__customer_program_execution_id",
        lambda _id: DummyCustomer(),
    )
    monkeypatch.setattr(
        "nadooit_os.views.check__active_customer_program_execution_manager_contract__exists__between__employee_and_customer",
        lambda employee, customer: True,
    )

    class DummyExec:
        pass

    monkeypatch.setattr(
        "nadooit_os.views.get__customer_program_execution__for__customer_program_execution_id",
        lambda _id: DummyExec(),
    )

    def fake_set_status(customer_program_execution, payment_status):
        sent["payment_status"] = payment_status

    monkeypatch.setattr(
        "nadooit_os.views.set__payment_status__for__customer_program_execution",
        fake_set_status,
    )

    def fake_create(customer_program_execution, complaint, employee):
        sent["status"] = True
        sent["complainttext"] = complaint
        return True

    monkeypatch.setattr(
        "nadooit_os.views.create__customer_program_execution_complaint__for__customer_program_execution_and_complaint_and_employee",
        fake_create,
    )

    url = reverse(
        "nadooit_os:customer-program-execution-send-complaint",
        kwargs={"customer_program_execution_id": uuid.uuid4()},
    )
    resp = client.post(url, data={"complainttext": "bad charge"})
    assert resp.status_code == 200
    assert resp.content == b"ok"
    assert sent["status"] is True
    assert sent["payment_status"] == "REVOKED"
    assert sent["complainttext"] == "bad charge"
