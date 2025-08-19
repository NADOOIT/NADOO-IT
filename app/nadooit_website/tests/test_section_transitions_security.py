import os
from pathlib import Path

import pytest
from django.test import override_settings
from django.urls import reverse


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_serves_default_file_within_base_dir(client, tmp_path):
    # Arrange: create isolated BASE_DIR with allowed subdir and default file
    base_dir = tmp_path
    allowed_dir = base_dir / "nadooit_website" / "section_transition"
    allowed_dir.mkdir(parents=True, exist_ok=True)
    default_file = allowed_dir / "section_transitions.html"
    default_file.write_text("OK_DEFAULT", encoding="utf-8")

    with override_settings(BASE_DIR=str(base_dir)):
        # Act
        url = reverse("nadooit_website:section_transitions")
        resp = client.get(url)

    # Assert
    assert resp.status_code == 200
    assert resp["Content-Type"].startswith("text/html")
    assert resp.content.decode() == "OK_DEFAULT"


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_serves_group_file_slug_only(client, tmp_path):
    base_dir = tmp_path
    allowed_dir = base_dir / "nadooit_website" / "section_transition"
    allowed_dir.mkdir(parents=True, exist_ok=True)
    group_file = allowed_dir / "section_transitions_foo-bar.html"
    group_file.write_text("OK_GROUP", encoding="utf-8")

    with override_settings(BASE_DIR=str(base_dir)):
        url = reverse("nadooit_website:section_transitions_filtered", kwargs={"group_filter": "foo-bar"})
        resp = client.get(url)

    assert resp.status_code == 200
    assert resp.content.decode() == "OK_GROUP"


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_rejects_traversal_via_query_parameter(client, tmp_path):
    base_dir = tmp_path
    # Create an outside file to ensure it would be dangerous if read
    outside = base_dir / "outside.html"
    outside.write_text("SENSITIVE", encoding="utf-8")

    # Do not create any allowed files so we can see a 404/400
    (base_dir / "nadooit_website" / "section_transition").mkdir(parents=True, exist_ok=True)

    with override_settings(BASE_DIR=str(base_dir)):
        url = reverse("nadooit_website:section_transitions")
        # Attempt traversal using query parameter; should not be used
        resp = client.get(url, {"group_filter": "../../outside.html"})

    # Should not succeed; safe code returns 404 (missing default) or 400 (blocked)
    assert resp.status_code in {400, 404}


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_query_param_slug_is_respected_not_arbitrary_path(client, tmp_path):
    base_dir = tmp_path
    allowed_dir = base_dir / "nadooit_website" / "section_transition"
    allowed_dir.mkdir(parents=True, exist_ok=True)
    (allowed_dir / "section_transitions_abc.html").write_text("OK_ABC", encoding="utf-8")

    with override_settings(BASE_DIR=str(base_dir)):
        url = reverse("nadooit_website:section_transitions")
        resp = client.get(url, {"group_filter": "abc"})

    assert resp.status_code == 200
    assert resp.content.decode() == "OK_ABC"
