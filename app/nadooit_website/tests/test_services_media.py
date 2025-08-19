import os
import uuid
import pytest
from model_bakery import baker
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings as dj_settings

from nadooit_website.models import Video, VideoResolution, Section, File as SiteFile
from nadooit_website import services


@pytest.mark.django_db
def test_process_video_no_video_removes_tag_and_logs_warning(caplog):
    section = baker.make(Section, html="before {{ video }} after", video=None)

    out = services.process_video(section, section.html)

    assert "{{ video }}" not in out
    assert "before" in out and "after" in out
    # Warning is logged when no video but tag exists
    assert any("No video associated" in r.message for r in caplog.records)


@pytest.mark.django_db
def test_process_video_missing_hls_removes_tag_and_logs_warning(settings, tmp_path, caplog):
    settings.MEDIA_ROOT = tmp_path.as_posix()

    # Minimal video with required files
    preview = SimpleUploadedFile("preview.jpg", b"img")
    original = SimpleUploadedFile("original.mp4", b"mp4")
    video = Video.objects.create(title="Test V", preview_image=preview, original_file=original)

    # Only 480p present; 720/1080 missing => should remove tag
    vf = SimpleUploadedFile("480.mp4", b"data")
    hls = SimpleUploadedFile("index.m3u8", b"#EXTM3U\n")
    VideoResolution.objects.create(video=video, resolution=480, video_file=vf, hls_playlist_file=hls)

    section = baker.make(Section, html="X {{ video }} Y", video=video)

    out = services.process_video(section, section.html)

    assert "{{ video }}" not in out
    assert "X" in out and "Y" in out
    assert any("Not all HLS playlist files exist" in r.message for r in caplog.records)


@pytest.mark.django_db
def test_process_video_all_resolutions_inserts_embed(monkeypatch, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path.as_posix()

    # Fake template rendering
    monkeypatch.setattr(services, "render_to_string", lambda tpl, ctx: "<EMBED>")

    preview = SimpleUploadedFile("preview.jpg", b"img")
    original = SimpleUploadedFile("original.mp4", b"mp4")
    video = Video.objects.create(title="Test V", preview_image=preview, original_file=original)

    for res in (480, 720, 1080):
        vf = SimpleUploadedFile(f"{res}.mp4", b"v")
        hls = SimpleUploadedFile("master.m3u8", b"#EXTM3U\n")
        VideoResolution.objects.create(video=video, resolution=res, video_file=vf, hls_playlist_file=hls)

    section = baker.make(Section, html="A {{ video }} B", video=video)

    out = services.process_video(section, section.html)

    assert "<EMBED>" in out
    assert "{{ video }}" not in out


@pytest.mark.django_db
def test_process_file_tag_with_file_inserts_button(monkeypatch, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path.as_posix()
    # Fake template rendering
    monkeypatch.setattr(services, "render_to_string", lambda tpl, ctx: "<BTN>")

    # Create stored file
    uploaded = SimpleUploadedFile("doc.pdf", b"pdfdata")
    site_file = SiteFile.objects.create(name="Doc", file=uploaded)

    section = baker.make(Section, html="C {{ file }} D", file=site_file)

    out = services.process_file(section, section.html)

    assert "<BTN>" in out
    assert "{{ file }}" not in out


@pytest.mark.django_db
def test_process_file_tag_without_file_removes_tag_and_logs(caplog):
    section = baker.make(Section, html="E {{ file }} F", file=None)

    out = services.process_file(section, section.html)

    assert "{{ file }}" not in out
    assert any("No file associated" in r.message for r in caplog.records)


@pytest.mark.django_db
def test_process_file_no_tag_but_has_file_logs_warning(settings, tmp_path, caplog):
    settings.MEDIA_ROOT = tmp_path.as_posix()
    uploaded = SimpleUploadedFile("doc.txt", b"x")
    site_file = SiteFile.objects.create(name="Doc", file=uploaded)

    section = baker.make(Section, html="no tag here", file=site_file)

    out = services.process_file(section, section.html)

    assert out == "no tag here"
    assert any("but the { file } tag is missing" in r.message for r in caplog.records)
