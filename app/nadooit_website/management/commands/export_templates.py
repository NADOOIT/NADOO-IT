# nadooit_website/management/commands/export_templates.py
import os
import json
from django.db import models
from django.core.management.base import BaseCommand
from django.conf import settings
from nadooit_website.models import Plugin
from nadooit_website.models import Section


class Command(BaseCommand):
    help = "Export templates from the database to the filesystem"

    def add_arguments(self, parser):
        output_dir = os.path.join(
            settings.BASE_DIR, "nadooit_website", "templates_sync"
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

        # Export section templates
        for template in Section.objects.all():
            self.export_template(template, output_dir, "sections_templates")

        # Export plugin templates
        for plugin in Plugin.objects.all():
            self.export_template(plugin, output_dir, "plugins_templates")

        self.stdout.write(self.style.SUCCESS("Successfully exported templates"))

    def export_template(self, template, output_dir, subdirectory):
        template_name = template.name.replace(" ", "_")
        template_file_name = template_name + ".html"
        config_file_name = template_name + ".json"

        template_file_name = "".join(
            c for c in template_file_name if c.isalnum() or c in "._- "
        )
        config_file_name = "".join(
            c for c in config_file_name if c.isalnum() or c in "._- "
        )

        output_path = os.path.join(output_dir, subdirectory, template_file_name)
        config_output_path = os.path.join(output_dir, subdirectory, config_file_name)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w") as f:
            f.write(template.html)

        config_data = {}

        for field in template._meta.fields:
            field_value = getattr(template, field.name)
            if isinstance(field_value, (models.query.QuerySet, models.Manager)):
                field_value = [str(item) for item in field_value.all()]
            else:
                field_value = str(field_value)
            config_data[field.name] = field_value

        with open(config_output_path, "w") as f:
            json.dump(config_data, f, indent=4)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully exported template "{template}" to "{output_path}" and "{config_output_path}"'
            )
        )
