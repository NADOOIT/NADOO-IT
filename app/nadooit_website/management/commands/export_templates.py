# nadooit_website/management/commands/export_templates.py
import os
from django.core.management.base import BaseCommand
from django.conf import settings

from nadooit_website.models import Section


class Command(BaseCommand):
    help = "Export templates from the database to the filesystem"

    def add_arguments(self, parser):
        output_dir = os.path.join(
            settings.BASE_DIR, "nadooit_website", "sections_templates"
        )
        parser.add_argument(
            "--output-dir",
            type=str,
            default=output_dir,
            help="Output directory for the exported templates",
        )

    def handle(self, *args, **options):
        output_dir = options["output_dir"]
        os.makedirs(output_dir, exist_ok=True)

        for template in Section.objects.all():
            template_file_name = template.section_name.replace(" ", "_") + ".html"
            # make sure that the file name is a valid file name

            template_file_name = "".join(
                c for c in template_file_name if c.isalnum() or c in "._- "
            )

            output_path = os.path.join(output_dir, template_file_name)

            # Create any necessary subdirectories
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with open(output_path, "w") as f:
                f.write(template.section_html)

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully exported template "{template.section_name}" to "{output_path}"'
                )
            )
