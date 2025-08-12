import os
import pytest
from django.core.management import call_command
from django.conf import settings
from model_bakery import baker

from nadooit_website.models import Section, Plugin


@pytest.mark.django_db
def test_section_name_sanitized_on_save():
    raw_name = "Hello*!/\\Name"
    s = Section.objects.create(name=raw_name, html="<div></div>")
    # Model save() should sanitize name to only allowed characters
    allowed = set("._- ")
    assert all(c.isalnum() or c in allowed for c in s.name)
    # It should remove the disallowed characters from raw name
    expected = "".join(c for c in raw_name if c.isalnum() or c in allowed)
    assert s.name == expected


@pytest.mark.django_db
def test_export_import_templates_round_trip(tmp_path, settings):
    # Arrange: create one Section and one Plugin
    section = Section.objects.create(name="Landing Section", html="<h1>Hi</h1>")
    plugin = Plugin.objects.create(name="CTA Button", html="<button>Go</button>")

    out_dir = tmp_path / "templates_sync"

    # Act: export to filesystem
    call_command("export_templates", "--output-dir", str(out_dir))

    # Assert: files created
    sec_html = out_dir / "sections_templates" / "Landing_Section.html"
    plug_html = out_dir / "plugins_templates" / "CTA_Button.html"
    assert sec_html.exists()
    assert plug_html.exists()
    assert sec_html.read_text() == section.html
    assert plug_html.read_text() == plugin.html

    # Remove DB objects
    Section.objects.all().delete()
    Plugin.objects.all().delete()

    # Act: import back from filesystem
    call_command("import_templates", "--input-dir", str(out_dir))

    # Assert: objects recreated with same HTML
    s2 = Section.objects.get(name="Landing_Section")
    p2 = Plugin.objects.get(name="CTA_Button")
    assert s2.html == "<h1>Hi</h1>"
    assert p2.html == "<button>Go</button>"
