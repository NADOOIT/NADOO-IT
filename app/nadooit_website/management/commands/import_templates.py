# nadooit_website/management/commands/import_templates.py
import os
import json
import uuid
import chardet
from django.core.management.base import BaseCommand
from django.conf import settings

from nadooit_website.models import Section, Plugin


class Command(BaseCommand):
    help = "Import templates from the filesystem into the database"

    def add_arguments(self, parser):
        input_dir = os.path.join(settings.BASE_DIR, "nadooit_website", "templates_sync")
        parser.add_argument(
            "--input-dir",
            type=str,
            default=input_dir,
            help="Input directory for the templates to import",
        )

    def is_valid_filename(self, filename):
        return all(c.isalnum() or c in "._- " for c in filename)

    def get_valid_filename(self, filename):
        return "".join(c for c in filename if c.isalnum() or c in "._- ")

    def handle(self, *args, **options):
        input_dir = options["input_dir"]

        for root, dirs, files in os.walk(input_dir):
            for filename in files:
                if filename.endswith(".html"):
                    file_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(file_path, input_dir)
                    subdirectory, template_name = os.path.split(rel_path)
                    template_name = template_name[:-5]  # Remove .html extension

                    content = None

                    # Read the file with UTF-8 encoding
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                    except UnicodeDecodeError:
                        # Fall back to using cchardet if UTF-8 decoding fails
                        with open(file_path, "rb") as f:
                            raw_data = f.read()
                            encoding = chardet.detect(raw_data)["encoding"]

                        with open(file_path, "r", encoding=encoding) as f:
                            content = f.read()

                    # Attempt to load adjacent JSON metadata for stable IDs
                    json_path = os.path.join(root, f"{template_name}.json")
                    meta = {}
                    if os.path.exists(json_path):
                        try:
                            with open(json_path, "r", encoding="utf-8") as jf:
                                meta = json.load(jf)
                        except Exception:
                            meta = {}

                    if subdirectory == "sections_templates":
                        # Prefer fixed UUID from JSON if present
                        sec_uuid = None
                        raw_uuid = meta.get("section_id") or meta.get("id")
                        if raw_uuid:
                            try:
                                sec_uuid = uuid.UUID(str(raw_uuid))
                            except Exception:
                                sec_uuid = None

                        if sec_uuid:
                            Section.objects.update_or_create(
                                section_id=sec_uuid,
                                defaults={
                                    "name": template_name,
                                    "html": content,
                                },
                            )
                        else:
                            Section.objects.update_or_create(
                                name=template_name,
                                defaults={"html": content},
                            )

                    elif subdirectory == "plugins_templates":
                        # Prefer fixed integer ID from JSON if present
                        raw_pid = meta.get("id")
                        pk_int = None
                        try:
                            if raw_pid is not None:
                                pk_int = int(raw_pid)
                        except (TypeError, ValueError):
                            pk_int = None

                        if pk_int is not None:
                            # If an object with this PK exists, update; else create with explicit PK
                            try:
                                obj = Plugin.objects.get(pk=pk_int)
                                obj.name = template_name
                                obj.html = content
                                obj.save()
                            except Plugin.DoesNotExist:
                                Plugin.objects.create(id=pk_int, name=template_name, html=content)
                        else:
                            Plugin.objects.update_or_create(
                                name=template_name,
                                defaults={"html": content},
                            )
                    else:
                        raise ValueError(f"Unknown subdirectory: {subdirectory}")

                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully imported template "{template_name}"'
                        )
                    )
