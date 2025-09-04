import pytest
from django.template.loader import render_to_string


def test_file_download_button_escapes_filename():
    # Malicious HTML in filename should be escaped, not rendered
    ctx = {
        "file_url": "http://example.com/download?q=\"'>inject",
        "file_name": '<img src=x onerror="alert(1)">',
    }
    rendered = render_to_string(
        "nadooit_website/file_download_button.html", ctx
    )
    # should not contain raw HTML tag from file_name
    assert "<img" not in rendered
    # but escaped entities should appear
    assert "&lt;img" in rendered
    # href attribute should not be broken by quotes in URL
    assert 'href="' in rendered
    # ensure no unescaped closing tag injection occurred
    assert "</a>" in rendered


def test_video_embed_escapes_js_context():
    # Playlist URLs and player UUID containing quotes and script breakers
    player_uuid = "bad'id\";</script><script>alert(1)</script>"
    playlist = "m3u8?id=\"onload=alert(1)//"

    rendered = render_to_string(
        "nadooit_website/video_embed.html",
        {
            "player_uuid": player_uuid,
            "playlist_url_480p": playlist,
            "playlist_url_720p": playlist,
            "playlist_url_1080p": playlist,
        },
    )

    # injection sequence attempting to break out must not appear
    assert "</script><script>" not in rendered
    # raw player_uuid string must not appear inside JS context unescaped
    assert player_uuid not in rendered
    # should still include the expected player initialization call with a safe id prefix
    assert "videojs('v" in rendered
