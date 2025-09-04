import pytest
from model_bakery import baker

from nadooit_auth.custom_user_code_auth_backend import UserCodeBackend


@pytest.mark.django_db
class TestUserCodeBackend:
    def test_authenticate_returns_user_for_valid_code(self):
        user = baker.make("nadooit_auth.User", user_code="CODE123")
        backend = UserCodeBackend()

        result = backend.authenticate(request=None, user_code="CODE123")

        assert result is not None
        assert result.id == user.id

    def test_authenticate_returns_none_for_invalid_code(self):
        baker.make("nadooit_auth.User", user_code="CODE123")
        backend = UserCodeBackend()

        result = backend.authenticate(request=None, user_code="NOPE")

        assert result is None

    def test_get_user(self):
        user = baker.make("nadooit_auth.User", user_code="CODE999")
        backend = UserCodeBackend()

        assert backend.get_user("CODE999").id == user.id
        assert backend.get_user("MISSING") is None
