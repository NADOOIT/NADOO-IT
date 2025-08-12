import pytest
from django.urls import reverse
from django.test import Client

from nadooit_website.models import ContentPage


@pytest.mark.django_db
class TestContentPagesJSAndBase:
    def test_published_renders_js(self):
        ContentPage.objects.create(
            slug="with-js",
            title="With JS",
            html="<div id=\"x\">X</div>",
            css="",
            js="window.__x = 42;",
            is_published=True,
        )
        url = reverse("nadooit_website:content_page", args=["with-js"])
        c = Client()
        resp = c.get(url)
        assert resp.status_code == 200
        html = resp.content.decode("utf-8")
        assert "window.__x = 42;" in html
        assert "<script>" in html

    def test_base_title_overridden_by_page_title_and_session_id_guard(self):
        ContentPage.objects.create(
            slug="title-test",
            title="My Title",
            html="<h1>Hi</h1>",
            css="",
            js="",
            is_published=True,
        )
        url = reverse("nadooit_website:content_page", args=["title-test"])
        c = Client()
        resp = c.get(url)
        assert resp.status_code == 200
        html = resp.content.decode("utf-8")
        assert "<title>My Title</title>" in html
        # session_id is not provided by content_page view; ensure it is safely defaulted
        assert 'data-session-id=""' in html
