import pytest
from django.urls import reverse
from django.test import Client

from nadooit_website.models import ContentPage


@pytest.mark.django_db
class TestContentPages:
    def test_unpublished_returns_404(self):
        ContentPage.objects.create(
            slug="draft", title="Draft", html="<h1>Draft</h1>", css="h1{color:red}", is_published=False
        )
        url = reverse("nadooit_website:content_page", args=["draft"])
        c = Client()
        resp = c.get(url)
        assert resp.status_code == 404

    def test_published_renders_html_and_css(self):
        ContentPage.objects.create(
            slug="hello",
            title="Hello",
            html="<h1 id=\"title\">Hello World</h1>",
            css="#title{color:rgb(1,2,3)}",
            is_published=True,
        )
        url = reverse("nadooit_website:content_page", args=["hello"])
        c = Client()
        resp = c.get(url)
        assert resp.status_code == 200
        html = resp.content.decode("utf-8")
        assert "Hello World" in html
        # CSS is injected via style tag
        assert "rgb(1,2,3)" in html
