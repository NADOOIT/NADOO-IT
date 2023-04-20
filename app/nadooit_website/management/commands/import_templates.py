# nadooit_website/management/commands/import_templates.py
import os
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

                    if subdirectory == "sections_templates":
                        model_class = Section
                    elif subdirectory == "plugins_templates":
                        model_class = Plugin
                    else:
                        raise ValueError(f"Unknown subdirectory: {subdirectory}")

                    model_class.objects.update_or_create(
                        name=template_name,
                        defaults={"html": content},
                    )

                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully imported template "{template_name}"'
                        )
                    )
