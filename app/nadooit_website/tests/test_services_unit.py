import os
import zipfile
from pathlib import Path

import pytest

from nadooit_website.services import (
    get__session_tick,
    add__signal,
    zip_files,
    zip_directories_and_files,
)


def test_get_session_tick_positive_integer():
    tick = get__session_tick()
    assert isinstance(tick, int)
    assert tick > 0


@pytest.mark.parametrize(
    "signal_type",
    [
        "click",
        "mouseleave",
    ],
)
def test_add_signal_injects_script_and_attrs(signal_type):
    html = "<div>content</div>"
    session_id = "sess-123"
    section_id = "sec-456"

    out = add__signal(html, session_id, section_id, signal_type)

    # Wraps original html and appends a script block
    assert "<script>" in out and "</script>" in out
    # Includes the data attributes hook for the section
    assert f'data-session-id="{session_id}"' in out
    assert f'data-section-id="{section_id}"' in out


def test_add_signal_end_of_session_sections_htmx_div():
    html = "<div>content</div>"
    session_id = "sess-abc"
    section_id = "sec-def"

    out = add__signal(html, session_id, section_id, "end_of_session_sections")

    # Inserts an htmx-enabled div with a POST to the named URL
    assert "hx-post" in out
    assert "nadooit_website:end_of_session_sections" in out
    # Contains both IDs in the constructed URL
    assert session_id in out
    assert section_id in out
    # Keeps original content inside
    assert "<div>content</div>" in out


def _write(tmp_path: Path, rel: str, content: str = "x") -> Path:
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return p


def test_zip_directories_and_files_includes_expected_arcnames(tmp_path: Path):
    # Layout:
    # dirA/
    #   a.txt
    #   sub/
    #     b.txt
    # root.txt
    dirA = tmp_path / "dirA"
    f_a = _write(tmp_path, "dirA/a.txt", "A")
    f_b = _write(tmp_path, "dirA/sub/b.txt", "B")
    f_root = _write(tmp_path, "root.txt", "R")

    zip_path = tmp_path / "bundle.zip"
    zip_directories_and_files([str(dirA), str(f_root)], str(zip_path))

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = set(zf.namelist())

    # Files from dirA are stored relative to dirA/.. => include dirA prefix
    assert "dirA/a.txt" in names
    assert "dirA/sub/b.txt" in names
    # Single file gets stored under its basename
    assert "root.txt" in names


def test_zip_files_uses_full_paths_as_arcnames(tmp_path: Path):
    f1 = _write(tmp_path, "x.txt", "x")
    f2 = _write(tmp_path, "y/y.txt", "y")

    zip_path = tmp_path / "files.zip"
    zip_files([str(f1), str(f2)], str(zip_path))

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = set(zf.namelist())

    # zipfile strips leading root (e.g., '/'), so compare normalized paths
    normalized = {n.lstrip(os.sep) for n in names}
    assert str(f1).lstrip(os.sep) in normalized
    assert str(f2).lstrip(os.sep) in normalized
