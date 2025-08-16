# Website System Overview (Sections, Video & File Hosting)

This document explains how the NADOO-IT website system works, how content is composed from database-backed sections, and how to embed videos and files in sections.

Key modules and templates referenced:
- Python: `app/nadooit_website/services.py`
- Templates: `nadooit_website/video_embed.html`, `nadooit_website/file_download_button.html`, `nadooit_website/base.html`
- Management commands: `export_templates`, `import_templates`
- Docs: [Management Commands](management-commands.md)

---

## 1) Concept: Sections rendered from the database

The website is built from `Section` entries stored in the database. Each section has an HTML body (`section.html`) that may include special placeholders such as:
- `{{ video }}` – replaced with a responsive HLS player when a video is attached
- `{{ file }}` – replaced with a download button when a file is attached

The render flow (simplified) lives in `services.py`:
- `get__section_html_including_signals__for__section_and_session_id(section, session_id)`
  - Starts with `section.html`
  - Injects tracking/interaction signals
  - Replaces `{{ video }}` and `{{ file }}` with the appropriate embeds

---

## 2) Session and interaction signals

The system tracks lightweight interactions to improve UX analysis and dynamic behavior. In `services.py`, `add__signal(...)` injects behavior for several signal types:
- `end_of_session_sections` – posts a signal when the section becomes visible (htmx `hx-trigger="revealed"`)
- `click` – sends a POST when the user clicks within the section
- `mouseleave` – measures hover/interaction time between mouseenter/leave and posts it
- `vote` – injects two SVG buttons (up/down) and posts the selected vote

Signals are injected as `hx-post` fragments (htmx) or `fetch()` calls to endpoints like:
- `/signal/<session_id>/<section_id>/<signal_type>/`
- `/signal/<session_id>/<section_id>/click/` (etc.)

These are used to build a `Session`'s engagement profile server-side.

---

## 3) Embedding videos with quality selection (HLS + Video.js)

Prerequisites:
- A Video model related to the Section with generated HLS playlists for 480p, 720p, 1080p
- Each resolution has an `hls_playlist_file` available (e.g., `*.m3u8` served under MEDIA_URL)

How it renders:
1. `process_video(section, html)` checks that all three playlists exist.
2. If present, it obtains the three playlist URLs and calls `generate_video_embed_code(...)`.
3. That renders `nadooit_website/video_embed.html` with a unique `player_uuid` and the URLs.
4. The template uses Video.js and registers a simple quality selector to switch between the sources.
5. The resulting embed HTML replaces the `{{ video }}` placeholder in the section HTML.

Important includes:
- `nadooit_website/base.html` loads Video.js CSS/JS globally:
  - CSS: `static/videojs/video-js.min.css`
  - JS: `static/videojs/video.min.js`

Admin authoring steps (typical):
- Upload a video and generate/attach HLS playlists for 480/720/1080.
- In the Section admin, set the `video` relation to this video.
- In your section HTML, insert `{{ video }}` where the player should appear.

Troubleshooting:
- If `{{ video }}` remains empty, ensure all three playlists exist; otherwise `process_video` removes the tag and logs a warning.
- Check browser devtools for network errors (CORS, 404, content-type for `.m3u8`).

---

## 4) Embedding downloadable files

How it renders:
1. `process_file(section, html)` runs when `{{ file }}` is present in the section HTML.
2. If `section.file` is set, it renders `nadooit_website/file_download_button.html` with `file_name` and `file_url` and replaces the placeholder.
3. If no file is set, the placeholder is removed and a warning is logged.

Admin authoring steps:
- Upload your file in the admin and attach it to the Section (e.g., `section.file`).
- In your section HTML, place `{{ file }}` where you want a download button.

Security notes:
- The download button links directly to the file URL. If you need restricted access, enforce it at the storage layer or serve via authenticated views.

---

## 5) Templates, import/export workflow

Because the site content is section-based, you can keep canonical section templates in the repo and sync with the database using management commands:

```bash
# Export DB sections → templates folder
python manage.py export_templates

# Import templates folder → DB sections
python manage.py import_templates
```

These commands are also documented in `docs/running.md` for Docker Compose usage.

Notes
- The default sync folder used by the commands is `nadooit_website/templates_sync`.
- The `create_sections` command writes files to `nadooit_website/sections_templates`. You can either copy/move them into `templates_sync` or call `import_templates --input-dir nadooit_website/sections_templates` to bring them into the DB.
- There is no separate `import_section_orders` command; section ordering is managed via the Django admin using the `Section_Order_Sections_Through_Model` inline with move up/down actions.

---

## 6) Static and media files

From Django settings (`app/nadooit/settings.py`):
- `MEDIA_URL = "/static/media/"`
- `MEDIA_ROOT = "/vol/web/media/"`
- `STATIC_URL = "/static/static/"`
- `STATIC_ROOT = "/vol/web/static/"`

In production, Docker Compose mounts volumes so uploads persist across container restarts. Ensure that your reverse proxy serves `/static/` and `/media/` paths correctly.

---

## 7) Quick authoring checklist

- Add or edit a Section in the admin
- For videos: ensure HLS playlists (480/720/1080) exist and are attached, then put `{{ video }}` in the HTML
- For files: attach the file and put `{{ file }}` in the HTML
- Use the import/export commands to sync templates with DB as needed
- Verify interactions (vote, click, mouseleave) are firing in Network tab, and check server logs for warnings

---

## 8) Section ordering and experiments

Section ordering
- Model: `Section_Order` with a many-to-many to `Section` through `Section_Order_Sections_Through_Model`.
- The through model subclasses `OrderedModel` and adds an `order` field used for positioning.
- Admin: `Section_OrderAdmin` includes an inline `WebsiteSectionsOrderTabularInline` that shows each Section with move up/down links.

Reorder sections in the admin
1. Go to Admin → Section Orders.
2. Add or edit a Section Order.
3. In the inline, choose `section` rows and use the “move up/down” links to arrange.
4. Click Save.

Tips
- The inline is ordered by the `order` field automatically (`ordered_model` handles moves safely).
- You can create multiple `Section_Order` objects to run different flows.

Experiments
- Model: `ExperimentGroup` with fields like `name`, `section_order`, counters for `successful_sessions` / `total_sessions`.
- Assign different `Section_Order`s to groups to A/B test engagement.
- New sessions can be attached to a group and inherit its `section_order` (see `services.py` for assignment logic).

Troubleshooting
- If move links are missing in the admin, ensure `ordered_model` is installed and migrations have run.
- If sections don’t render in the expected order, verify the underlying through-model rows’ `order` values and that the queryset orders by `order`.

---

## 9) Known limitations & next steps

- HLS playlists must exist for all three resolutions; otherwise the video is omitted. A future enhancement could support partial fallback.
- Video quality selector is a simple custom component; you can swap for a more full-featured plugin if needed.
- Database default is SQLite; enabling CockroachDB requires environment configuration (see `docs/running.md`). A future migration script will ease Cockroach adoption when scaling.
