import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from nadooit_website.models import ContentPage


@pytest.mark.django_db
class TestContentPagePreview:
    def test_preview_requires_login_and_staff(self, settings):
        settings.LOGIN_URL = "/auth/login-user"
        page = ContentPage.objects.create(
            slug="draft-preview",
            title="Draft Preview",
            html="<p>draft</p>",
            css="",
            js="",
            is_published=False,
        )
        url = reverse("nadooit_website:content_page_preview", args=[page.slug])

        c = Client()
        # Anonymous → redirect to login
        resp = c.get(url)
        assert resp.status_code == 302
        assert settings.LOGIN_URL in resp.headers.get("Location", "")

        # Authenticated non-staff → 403
        User = get_user_model()
        user = User.objects.create_user(username="u1", password="x")
        assert c.login(username="u1", password="x") is True
        resp = c.get(url)
        assert resp.status_code == 403

        # Staff → 200
        user.is_staff = True
        user.save()
        resp = c.get(url)
        assert resp.status_code == 200
        html = resp.content.decode("utf-8")
        assert "draft" in html


@pytest.mark.django_db
class TestContentPageManage:
    def _grant_perm(self, user, codename):
        ct = ContentType.objects.get_for_model(ContentPage)
        perm = Permission.objects.get(content_type=ct, codename=codename)
        user.user_permissions.add(perm)

    def test_manage_list_requires_any_perm(self):
        User = get_user_model()
        user = User.objects.create_user(username="viewer", password="x")
        c = Client()
        assert c.login(username="viewer", password="x") is True

        url = reverse("nadooit_website:manage_content_pages")
        resp = c.get(url)
        assert resp.status_code == 403

        # Grant view permission → allowed
        self._grant_perm(user, "view_contentpage")
        resp = c.get(url)
        assert resp.status_code == 200

    def test_manage_new_requires_add_perm(self):
        User = get_user_model()
        user = User.objects.create_user(username="adder", password="x")
        c = Client()
        assert c.login(username="adder", password="x") is True

        url = reverse("nadooit_website:manage_content_page_new")
        resp = c.get(url)
        assert resp.status_code == 403

        self._grant_perm(user, "add_contentpage")
        resp = c.get(url)
        assert resp.status_code == 200
        # POST create
        resp = c.post(
            url,
            {
                "title": "P1",
                "slug": "p1",
                "html": "<h1>H</h1>",
                "css": "h1{color:blue}",
                "js": "console.log('ok')",
                "is_published": True,
            },
        )
        assert resp.status_code in (302, 303)
        assert ContentPage.objects.filter(slug="p1").exists()

    def test_manage_edit_requires_change_perm(self):
        page = ContentPage.objects.create(
            slug="to-edit",
            title="Edit me",
            html="<p>old</p>",
            css="",
            js="",
            is_published=True,
        )
        User = get_user_model()
        user = User.objects.create_user(username="changer", password="x")
        c = Client()
        assert c.login(username="changer", password="x") is True

        url = reverse("nadooit_website:manage_content_page_edit", args=[page.slug])
        resp = c.get(url)
        assert resp.status_code == 403

        self._grant_perm(user, "change_contentpage")
        resp = c.get(url)
        assert resp.status_code == 200

        # POST update
        resp = c.post(
            url,
            {
                "title": "Edited",
                "slug": "to-edit",
                "html": "<p>new</p>",
                "css": "p{color:red}",
                "js": "window.changed=1;",
                "is_published": True,
            },
        )
        assert resp.status_code in (302, 303)
        page.refresh_from_db()
        assert page.title == "Edited"
        assert "new" in page.html
