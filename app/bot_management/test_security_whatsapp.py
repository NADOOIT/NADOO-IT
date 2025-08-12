import pytest
from django.urls import reverse
from django.conf import settings

# Skip this module unless WhatsApp is explicitly enabled.
pytestmark = pytest.mark.skipif(
    not getattr(settings, "WHATSAPP_ENABLED", False),
    reason="WhatsApp integration is disabled by default. Set WHATSAPP_ENABLED=1 to run these tests.",
)


@pytest.mark.django_db
def test_whatsapp_webhook_echoes_challenge_as_plain_text(client):
    # known bot id from code (registered by decorator on import)
    bot_id = "3cfa80bb-f3c1-49ff-bf1d-2f51f5f22138"
    url = reverse("bot_management:whatsapp-webhook", args=[bot_id])

    challenge = "1382766763"
    resp = client.get(url, {"hub.challenge": challenge})

    # Desired hardened behavior: echo only and as text/plain
    assert resp.status_code == 200
    assert resp.content.decode() == challenge
    assert resp["Content-Type"].startswith("text/plain")


@pytest.mark.django_db
def test_whatsapp_webhook_rejects_html_in_challenge(client):
    bot_id = "3cfa80bb-f3c1-49ff-bf1d-2f51f5f22138"
    url = reverse("bot_management:whatsapp-webhook", args=[bot_id])

    xss_payload = "<script>alert(1)</script>"
    resp = client.get(url, {"hub.challenge": xss_payload})

    # Desired hardened behavior: reject unsafe content
    assert resp.status_code in {400, 422}
    assert xss_payload not in resp.content.decode()


@pytest.mark.django_db
def test_whatsapp_webhook_missing_challenge_returns_400(client):
    bot_id = "3cfa80bb-f3c1-49ff-bf1d-2f51f5f22138"
    url = reverse("bot_management:whatsapp-webhook", args=[bot_id])

    resp = client.get(url)

    assert resp.status_code in {400, 422}
