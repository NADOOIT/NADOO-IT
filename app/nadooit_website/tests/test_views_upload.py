import io
import zipfile
import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.fixture
def staff_user(db):
    User = get_user_model()
    return User.objects.create_user(
        username="staff", email="staff@example.com", password="pw", is_staff=True
    )


@pytest.fixture
def normal_user(db):
    User = get_user_model()
    return User.objects.create_user(
        username="user", email="user@example.com", password="pw", is_staff=False
    )


def make_dummy_zip(filename="video.zip"):
    # Create an in-memory zip file (content doesn't matter for view-level tests)
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, mode="w") as zf:
        zf.writestr("dummy.txt", "ok")
    mem.seek(0)
    return SimpleUploadedFile(filename, mem.read(), content_type="application/zip")


def test_upload_requires_login_and_staff(db, client, normal_user):
    # Anonymous -> redirect to login
    resp = client.get(reverse("nadooit_website:video_upload"))
    assert resp.status_code in (301, 302)

    # Authenticated non-staff -> redirected to login (staff gate)
    client.force_login(normal_user)
    resp = client.get(reverse("nadooit_website:video_upload"))
    assert resp.status_code in (301, 302)


def test_upload_success_flow(db, client, staff_user, monkeypatch):
    client.force_login(staff_user)

    called = {"ok": False}

    def _handle(file):
        called["ok"] = True

    import nadooit_website.views as website_views

    monkeypatch.setattr(website_views, "handle_uploaded_file", _handle)

    file = make_dummy_zip()
    resp = client.post(
        reverse("nadooit_website:video_upload"),
        data={"file": file},
        format="multipart",
    )
    # Redirect to admin changelist on success
    assert resp.status_code in (301, 302)
    assert called["ok"] is True


def test_upload_failure_flow(db, client, staff_user, monkeypatch):
    client.force_login(staff_user)

    def _handle_raises(file):
        raise RuntimeError("boom")

    import nadooit_website.views as website_views

    monkeypatch.setattr(website_views, "handle_uploaded_file", _handle_raises)

    file = make_dummy_zip()
    resp = client.post(
        reverse("nadooit_website:video_upload"),
        data={"file": file},
        format="multipart",
    )
    # Still redirects to admin changelist, but with error message flashed by the view
    assert resp.status_code in (301, 302)
