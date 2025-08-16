import pytest
from django.test import RequestFactory
from django.urls import reverse

from nadooit_auth.views import _is_safe_redirect, safe_redirect


@pytest.mark.django_db
def test_is_safe_redirect_blocks_external_host():
    rf = RequestFactory()
    request = rf.get("/auth/login-user")
    # Simulate current host
    request._get_scheme = lambda: "http"
    request.is_secure = lambda: False
    request.META["HTTP_HOST"] = "testserver"

    assert _is_safe_redirect(request, "https://evil.com/path") is False
    assert _is_safe_redirect(request, "//evil.com/path") is False


@pytest.mark.django_db
def test_is_safe_redirect_allows_relative_paths():
    rf = RequestFactory()
    request = rf.get("/auth/login-user")
    request._get_scheme = lambda: "http"
    request.is_secure = lambda: False
    request.META["HTTP_HOST"] = "testserver"

    assert _is_safe_redirect(request, "/nadooit-os") is True
    assert _is_safe_redirect(request, "/some/internal/page") is True


@pytest.mark.django_db
def test_safe_redirect_defaults_on_external_target():
    rf = RequestFactory()
    request = rf.get("/auth/login-user")
    request._get_scheme = lambda: "http"
    request.is_secure = lambda: False
    request.META["HTTP_HOST"] = "testserver"

    resp = safe_redirect(request, "https://evil.com/path")
    assert resp.status_code == 302
    assert resp.url == reverse("nadooit_os:nadooit-os")


@pytest.mark.django_db
def test_safe_redirect_uses_relative_target():
    rf = RequestFactory()
    request = rf.get("/auth/login-user")
    request._get_scheme = lambda: "http"
    request.is_secure = lambda: False
    request.META["HTTP_HOST"] = "testserver"

    resp = safe_redirect(request, "/foo")
    assert resp.status_code == 302
    assert resp.url == "/foo"
