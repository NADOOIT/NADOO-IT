# Management Commands

This page catalogs useful Django management commands provided by NADOO-IT for operating the Website/Sections system and related tooling.

Location
- Commands live under `app/nadooit_website/management/commands/`

## Templates export/import

Export templates from the database to the filesystem
```bash
docker compose -f docker-compose-dev.yml run --rm app \
  python manage.py export_templates \
  --output-dir app/nadooit_website/templates_sync
```
- Default output directory (inside the repo): `nadooit_website/templates_sync`

Import templates from the filesystem into the database
```bash
docker compose -f docker-compose-dev.yml run --rm app \
  python manage.py import_templates \
  --input-dir app/nadooit_website/templates_sync
```
- Default input directory: `nadooit_website/templates_sync`
- Run this after editing files in the templates sync folder so changes are loaded into the DB.

Notes on directories
- `export_templates`/`import_templates` default to `nadooit_website/templates_sync`.
- The `create_sections` command (below) writes files to `nadooit_website/sections_templates`. If you want to import those into the DB, either move/copy them into `templates_sync` or pass `--input-dir` to `import_templates` to point at `sections_templates`.

## Generate section templates from JSON

Create basic section HTML files from `nadooit_website/input/sections.json`.
```bash
docker compose -f docker-compose-dev.yml run --rm app \
  python manage.py create_sections
```
- Output directory: `nadooit_website/sections_templates`
- After generation, import the templates into the DB (see above) if you plan to render sections from the database.

## Embeddings tooling (optional)

Prepare embedding data and train embeddings used by search/recommendations.
```bash
# Prepare data
docker compose -f docker-compose-dev.yml run --rm app \
  python manage.py prepare_embedding_data

# Train
docker compose -f docker-compose-dev.yml run --rm app \
  python manage.py train_embeddings
```

## Typical workflows

Sync DB → Filesystem (backup or version control)
```bash
python manage.py export_templates
```
Filesystem → DB (after editing templates)
```bash
python manage.py import_templates
```
Create starter templates from JSON, then import to DB
```bash
python manage.py create_sections
python manage.py import_templates --input-dir app/nadooit_website/sections_templates
```

See also
- Website System: `docs/website-system.md`
- Running guide: `docs/running.md`
