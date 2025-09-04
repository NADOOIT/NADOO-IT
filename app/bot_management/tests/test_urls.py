import importlib
import pytest
from django.conf import settings
from django.test import override_settings
from django.urls import clear_url_caches, resolve
from django.urls.exceptions import Resolver404


@pytest.mark.django_db
@override_settings(WHATSAPP_ENABLED=False)
def test_whatsapp_url_absent_when_disabled(settings):
    # Ensure URL resolver reloads with updated setting
    clear_url_caches()
    import bot_management.urls  # noqa: F401
    importlib.reload(bot_management.urls)
    import nadooit.urls  # noqa: F401
    importlib.reload(nadooit.urls)

    with pytest.raises(Resolver404):
        resolve("/bot/whatsapp/webhook/dummy-id")


@pytest.mark.django_db
@override_settings(WHATSAPP_ENABLED=True)
def test_whatsapp_url_present_when_enabled(settings):
    clear_url_caches()
    import bot_management.urls  # noqa: F401
    importlib.reload(bot_management.urls)
    import nadooit.urls  # noqa: F401
    importlib.reload(nadooit.urls)

    match = resolve("/bot/whatsapp/webhook/3cfa80bb-f3c1-49ff-bf1d-2f51f5f22138")
    assert match.url_name == "whatsapp-webhook"
