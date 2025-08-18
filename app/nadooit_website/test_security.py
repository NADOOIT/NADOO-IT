import io
import zipfile
import json
import os
import pytest
import uuid

from nadooit_website.services import handle_uploaded_file
from django.urls import reverse


@pytest.mark.django_db
def test_handle_uploaded_file_blocks_zip_path_traversal(monkeypatch, settings, tmp_path):
    # Prepare an in-memory zip with a traversal entry and minimal required structure
    zip_bytes = io.BytesIO()
    with zipfile.ZipFile(zip_bytes, mode="w") as zf:
        # Required metadata file
        video_meta = {
            "id": str(uuid.uuid4()),
            "title": "test",
            "preview_image": "../../evil.png",
            "original_file": "../../orig.mp4",
            "resolutions": [],
        }
        zf.writestr("video_data.json", json.dumps(video_meta))
        # Malicious entries attempting to escape the extraction directory
        zf.writestr("../../evil.png", b"pngdata")
        zf.writestr("../../orig.mp4", b"mp4data")

    zip_bytes.seek(0)

    # Ensure MEDIA_ROOT points to a temp folder for isolation (even though tests are not run)
    settings.MEDIA_ROOT = str(tmp_path)

    # Monkeypatch to fail fast if extractall receives traversal members
    original_zipfile_cls = zipfile.ZipFile

    class GuardedZipFile(original_zipfile_cls):
        def extractall(self, path=None, members=None, pwd=None):
            names = self.namelist() if members is None else members
            if any(".." in name or name.startswith("/") for name in names):
                raise AssertionError("Unsafe zip path detected; extraction should be sanitized")
            return super().extractall(path=path, members=members, pwd=pwd)

    monkeypatch.setattr(zipfile, "ZipFile", GuardedZipFile)

    # Expectation: safe implementation raises ValueError when traversal is detected
    with pytest.raises(ValueError):
        handle_uploaded_file(zip_bytes)


@pytest.mark.django_db
def test_section_transitions_serves_slug_file(client, settings, tmp_path):
    # Prepare a safe HTML file for a valid slug
    base_dir = tmp_path / "nadooit_website" / "section_transition"
    base_dir.mkdir(parents=True, exist_ok=True)
    html_path = base_dir / "section_transitions_foo.html"
    html_path.write_text("OK-FOO", encoding="utf-8")

    # Point BASE_DIR to our temp project root
    settings.BASE_DIR = str(tmp_path)

    url = reverse("nadooit_website:section_transitions_filtered", args=["foo"])
    resp = client.get(url)
    assert resp.status_code == 200
    assert b"OK-FOO" in resp.content


@pytest.mark.django_db
def test_section_transitions_blocks_traversal_and_falls_back_to_default(client, settings, tmp_path):
    # Create only the default file, not a specific group file
    base_dir = tmp_path / "nadooit_website" / "section_transition"
    base_dir.mkdir(parents=True, exist_ok=True)
    default_html = base_dir / "section_transitions.html"
    default_html.write_text("DEFAULT", encoding="utf-8")

    settings.BASE_DIR = str(tmp_path)

    # Use query parameter with traversal attempt; should ignore and serve default file
    url = reverse("nadooit_website:section_transitions") + "?group_filter=../evil"
    resp = client.get(url)
    assert resp.status_code == 200
    assert b"DEFAULT" in resp.content


@pytest.mark.django_db
def test_section_transitions_missing_file_returns_404(client, settings, tmp_path):
    # No files created; requesting a slug should return 404
    settings.BASE_DIR = str(tmp_path)
    url = reverse("nadooit_website:section_transitions_filtered", args=["doesnotexist"])  # sanitized, but file missing
    resp = client.get(url)
    assert resp.status_code == 404


@pytest.mark.django_db
def test_handle_uploaded_file_invalid_json_raises_and_cleans_tmp(settings, tmp_path):
    # Corrupt JSON should raise JSONDecodeError and cleanup temp dir
    zip_bytes = io.BytesIO()
    with zipfile.ZipFile(zip_bytes, mode="w") as zf:
        zf.writestr("video_data.json", "{ invalid json")

    zip_bytes.seek(0)
    settings.MEDIA_ROOT = str(tmp_path)

    temp_dir = os.path.join(settings.MEDIA_ROOT, "temp")
    with pytest.raises(json.JSONDecodeError):
        handle_uploaded_file(zip_bytes)
    assert not os.path.exists(temp_dir)


@pytest.mark.django_db
def test_handle_uploaded_file_missing_required_keys_raises_and_cleans_tmp(settings, tmp_path):
    # Missing 'id' should raise KeyError and cleanup temp dir
    zip_bytes = io.BytesIO()
    with zipfile.ZipFile(zip_bytes, mode="w") as zf:
        video_meta = {
            # 'id' missing
            "title": "missing-id",
            "resolutions": [],
        }
        zf.writestr("video_data.json", json.dumps(video_meta))

    zip_bytes.seek(0)
    settings.MEDIA_ROOT = str(tmp_path)

    temp_dir = os.path.join(settings.MEDIA_ROOT, "temp")
    with pytest.raises(KeyError):
        handle_uploaded_file(zip_bytes)
    assert not os.path.exists(temp_dir)


@pytest.mark.django_db
def test_handle_uploaded_file_missing_referenced_files_raises_and_cleans_tmp(settings, tmp_path):
    # Metadata references files that are not in the archive; should raise FileNotFoundError and cleanup temp dir
    zip_bytes = io.BytesIO()
    with zipfile.ZipFile(zip_bytes, mode="w") as zf:
        video_meta = {
            "id": str(uuid.uuid4()),
            "title": "missing-files",
            "preview_image": "images/missing.png",
            "original_file": "media/missing.mp4",
            "resolutions": [],
        }
        zf.writestr("video_data.json", json.dumps(video_meta))

    zip_bytes.seek(0)
    settings.MEDIA_ROOT = str(tmp_path)

    temp_dir = os.path.join(settings.MEDIA_ROOT, "temp")
    with pytest.raises(FileNotFoundError):
        handle_uploaded_file(zip_bytes)
    assert not os.path.exists(temp_dir)


@pytest.mark.django_db
def test_handle_uploaded_file_hls_dir_missing_is_ignored(settings, tmp_path):
    # If hls_playlist_file points to a non-existent dir, it should be ignored without raising
    zip_bytes = io.BytesIO()
    with zipfile.ZipFile(zip_bytes, mode="w") as zf:
        video_meta = {
            "id": str(uuid.uuid4()),
            "title": "no-hls-dir",
            "resolutions": [
                {
                    "id": 42,
                    "resolution": 480,
                    "video_file": "videos/vid.mp4",
                    "hls_playlist_file": "hls/missing_dir",  # not provided in archive
                }
            ],
        }
        zf.writestr("video_data.json", json.dumps(video_meta))
        zf.writestr("videos/vid.mp4", b"data")

    zip_bytes.seek(0)
    settings.MEDIA_ROOT = str(tmp_path)

    # Should not raise
    handle_uploaded_file(zip_bytes)


@pytest.mark.django_db
def test_handle_uploaded_file_blocks_nested_traversal(settings, tmp_path):
    # Attempt traversal via a nested path inside a subdirectory
    zip_bytes = io.BytesIO()
    with zipfile.ZipFile(zip_bytes, mode="w") as zf:
        video_meta = {
            "id": str(uuid.uuid4()),
            "title": "nested-traversal",
            "preview_image": "subdir/../../evil.png",
            "original_file": "subdir/../../orig.mp4",
            "resolutions": [],
        }
        zf.writestr("video_data.json", json.dumps(video_meta))
        zf.writestr("subdir/../../evil.png", b"pngdata")
        zf.writestr("subdir/../../orig.mp4", b"mp4data")

    zip_bytes.seek(0)
    settings.MEDIA_ROOT = str(tmp_path)

    with pytest.raises(ValueError):
        handle_uploaded_file(zip_bytes)


@pytest.mark.django_db
def test_handle_uploaded_file_allows_benign_zip(settings, tmp_path):
    # A benign archive with properly scoped relative paths should succeed
    zip_bytes = io.BytesIO()
    with zipfile.ZipFile(zip_bytes, mode="w") as zf:
        video_meta = {
            "id": str(uuid.uuid4()),
            "title": "benign",
            "preview_image": "images/preview.png",
            "original_file": "media/original.mp4",
            "resolutions": [
                {
                    "id": 20,
                    "resolution": 480,
                    "video_file": "videos/vid.mp4",
                    "hls_playlist_file": "hls/playlist",
                }
            ],
        }
        zf.writestr("video_data.json", json.dumps(video_meta))
        zf.writestr("images/preview.png", b"pngdata")
        zf.writestr("media/original.mp4", b"mp4data")
        zf.writestr("videos/vid.mp4", b"data")
        # benign HLS folder structure
        zf.writestr("hls/playlist/master.m3u8", b"#EXTM3U\n")

    zip_bytes.seek(0)
    settings.MEDIA_ROOT = str(tmp_path)

    # Should not raise
    handle_uploaded_file(zip_bytes)


@pytest.mark.django_db
def test_handle_uploaded_file_blocks_hls_playlist_traversal(settings, tmp_path):
    # In metadata, set hls_playlist_file to a traversal path
    zip_bytes = io.BytesIO()
    with zipfile.ZipFile(zip_bytes, mode="w") as zf:
        video_meta = {
            "id": str(uuid.uuid4()),
            "title": "hls-traversal",
            # omit preview_image/original_file so they are optional
            "resolutions": [
                {
                    "id": 10,
                    "resolution": 720,
                    "video_file": "vid.mp4",
                    "hls_playlist_file": "../../hls",  # traversal
                }
            ],
        }
        zf.writestr("video_data.json", json.dumps(video_meta))
        zf.writestr("vid.mp4", b"data")

    zip_bytes.seek(0)
    settings.MEDIA_ROOT = str(tmp_path)

    with pytest.raises(ValueError):
        handle_uploaded_file(zip_bytes)


@pytest.mark.django_db
def test_handle_uploaded_file_sanitizes_windows_backslashes(settings, tmp_path):
    # Backslash paths should be sanitized to safe filenames within extraction dir
    zip_bytes = io.BytesIO()
    with zipfile.ZipFile(zip_bytes, mode="w") as zf:
        video_meta = {
            "id": str(uuid.uuid4()),
            "title": "win-sanitized",
            "preview_image": "..\\..\\evil.png",
            "original_file": "..\\..\\orig.mp4",
            "resolutions": [],
        }
        zf.writestr("video_data.json", json.dumps(video_meta))
        zf.writestr("..\\..\\evil.png", b"pngdata")
        zf.writestr("..\\..\\orig.mp4", b"mp4data")

    zip_bytes.seek(0)
    settings.MEDIA_ROOT = str(tmp_path)

    # Should not raise; names are sanitized and contained
    handle_uploaded_file(zip_bytes)


@pytest.mark.django_db
def test_handle_uploaded_file_blocks_absolute_path_entries(settings, tmp_path):
    # Prepare an in-memory zip with absolute path entries
    zip_bytes = io.BytesIO()
    with zipfile.ZipFile(zip_bytes, mode="w") as zf:
        video_meta = {
            "id": str(uuid.uuid4()),
            "title": "abs-path",
            "preview_image": "/evil.png",
            "original_file": "/orig.mp4",
            "resolutions": [],
        }
        zf.writestr("video_data.json", json.dumps(video_meta))
        zf.writestr("/evil.png", b"pngdata")
        zf.writestr("/orig.mp4", b"mp4data")

    zip_bytes.seek(0)
    settings.MEDIA_ROOT = str(tmp_path)

    # Expectation: safe implementation raises ValueError when absolute paths are detected
    with pytest.raises(ValueError):
        handle_uploaded_file(zip_bytes)


@pytest.mark.django_db
def test_section_transitions_default_missing_returns_404(client, settings, tmp_path):
    # When default file is missing, view should return 404
    settings.BASE_DIR = str(tmp_path)
    url = reverse("nadooit_website:section_transitions")
    resp = client.get(url)
    assert resp.status_code == 404
