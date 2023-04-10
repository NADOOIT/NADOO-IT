# nadooit_website/management/commands/import_templates.py
import os
import shutil
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from nadooit_website.models import Section


class Command(BaseCommand):
    help = "Import templates from the filesystem into the database"

    def add_arguments(self, parser):
        input_dir = os.path.join(
            settings.BASE_DIR, "nadooit_website", "sections_templates"
        )
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
                    if not self.is_valid_filename(filename):
                        valid_filename = self.get_valid_filename(filename)

                        old_path = os.path.join(root, filename)
                        new_path = os.path.join(root, valid_filename)
                        shutil.move(old_path, new_path)
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Renamed file "{old_path}" to "{new_path}".'
                            )
                        )
                        filename = valid_filename

                    file_path = os.path.join(root, filename)
                    section_name = os.path.relpath(file_path, input_dir)

                    # Remove the '.html' extension from the section_name
                    section_name = section_name[:-5]

                    with open(file_path, "r") as f:
                        content = f.read()

                    Section.objects.update_or_create(
                        section_name=section_name,
                        defaults={"section_html": content},
                    )

                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully imported template "{section_name}"'
                        )
                    )
