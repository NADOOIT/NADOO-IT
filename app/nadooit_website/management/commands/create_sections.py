import json
import os
from uuid import uuid4

from django.core.management.base import BaseCommand
from django.conf import settings
from nadooit_website.models import Section


class Command(BaseCommand):
    help = "Create section templates from a JSON file"

    def handle(self, *args, **options):
        # Define the paths
        sections_json_path = os.path.join(
            settings.BASE_DIR, "nadooit_website", "input", "sections.json"
        )
        templates_dir = os.path.join(
            settings.BASE_DIR, "nadooit_website", "sections_templates"
        )

        # Load the sections data from the JSON file
        with open(sections_json_path, "r", encoding="utf-8") as f:
            sections_data = json.load(f)

        # Create a set to store the section names
        section_names = set()

        for section in sections_data["werbetexte"]:
            # Generate a unique ID using uuid4
            section_id = str(uuid4())
            section_name = section["name"].replace(" ", "_")
            text = section["text"]

            # Check if the section_name is unique
            if section_name in section_names:
                self.stdout.write(
                    self.style.WARNING(
                        f'Skipping section "{section_name}" since it has a duplicate name.'
                    )
                )
                continue

            # Check if the section_name already exists in the database
            if Section.objects.filter(section_name=section_name).exists():
                self.stdout.write(
                    self.style.WARNING(
                        f'Skipping section "{section_name}" since it already exists in the database.'
                    )
                )
                continue

            # Add the section_name to the set
            section_names.add(section_name)

            # Create a new section template
            section_template = f"""<section>
    <div class="banner">
        <div class="our-grantee-gold" data-aos="fade-up">
            <h1>{text}</h1>
        </div>
    </div>
</section>"""

            # Save the section template to the sections_templates folder
            template_file_name = section_name
            template_file_path = os.path.join(
                templates_dir, f"{template_file_name}.html"
            )
            with open(template_file_path, "w", encoding="utf-8") as f:
                f.write(section_template)

        self.stdout.write(
            self.style.SUCCESS("Successfully created sections from sections.json")
        )
