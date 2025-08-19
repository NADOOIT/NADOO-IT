# nadooit_website/management/commands/import_section_orders.py
import os
import json
import uuid
from typing import List, Union

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction

from nadooit_website.models import (
    Section,
    Plugin,
    Section_Order,
    Section_Order_Sections_Through_Model,
)


class Command(BaseCommand):
    help = "Import Section Orders from JSON files into the database"

    def add_arguments(self, parser):
        default_dir = os.path.join(
            settings.BASE_DIR, "nadooit_website", "templates_sync", "section_order_templates"
        )
        parser.add_argument(
            "--input-dir",
            type=str,
            default=default_dir,
            help="Directory containing Section Order JSON templates",
        )

    def handle(self, *args, **options):
        input_dir = options["input_dir"]
        if not os.path.isdir(input_dir):
            self.stdout.write(self.style.WARNING(f"Input directory not found: {input_dir}"))
            return

        files = [
            os.path.join(input_dir, f)
            for f in os.listdir(input_dir)
            if f.lower().endswith(".json")
        ]

        if not files:
            self.stdout.write(self.style.WARNING(f"No JSON files found in {input_dir}"))
            return

        imported = 0
        for fp in files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to read {fp}: {e}"))
                continue

            try:
                self._import_one(data)
                imported += 1
                self.stdout.write(self.style.SUCCESS(f"Imported Section Order from {os.path.basename(fp)}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to import {fp}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Section Orders imported: {imported}"))

    @transaction.atomic
    def _import_one(self, data: dict):
        # Supported fields: section_order_id (optional, UUID),
        # sections: list of section identifiers (UUID strings or names),
        # plugins: list of plugin identifiers (integer IDs or names)
        so_id = data.get("section_order_id") or data.get("id")
        sections: List[Union[str, dict]] = data.get("sections", [])
        plugins: List[Union[str, int, dict]] = data.get("plugins", [])

        # Resolve or create Section_Order
        if so_id:
            try:
                so_uuid = uuid.UUID(str(so_id))
            except Exception:
                so_uuid = None
        else:
            so_uuid = None

        if so_uuid:
            section_order, _created = Section_Order.objects.get_or_create(section_order_id=so_uuid)
        else:
            section_order = Section_Order.objects.create()

        # Clear existing relations to re-apply order
        Section_Order_Sections_Through_Model.objects.filter(section_order=section_order).delete()
        section_order.plugins.clear()

        # Attach sections in order
        order_idx = 0
        for entry in sections:
            sec = None
            # Allow formats: UUID string, name string, or dict with keys {section_id|name}
            if isinstance(entry, dict):
                raw_id = entry.get("section_id") or entry.get("id")
                raw_name = entry.get("name")
            else:
                raw_id = entry
                raw_name = None

            # Try UUID-based resolution first
            sec_uuid = None
            try:
                sec_uuid = uuid.UUID(str(raw_id)) if raw_id else None
            except Exception:
                sec_uuid = None

            if sec_uuid:
                try:
                    sec = Section.objects.get(section_id=sec_uuid)
                except Section.DoesNotExist:
                    sec = None

            # Fallback to name-based resolution
            if sec is None:
                name_try = raw_name if raw_name else (str(entry) if not isinstance(entry, dict) else None)
                if name_try:
                    try:
                        sec = Section.objects.get(name=name_try)
                    except Section.DoesNotExist:
                        # Try alt name with spaces/underscores swapped
                        alt_name = name_try.replace("_", " ") if "_" in name_try else name_try.replace(" ", "_")
                        try:
                            sec = Section.objects.get(name=alt_name)
                        except Section.DoesNotExist:
                            sec = None

            if not sec:
                self.stdout.write(self.style.WARNING(f"Section not found: {entry}; skipping"))
                continue

            Section_Order_Sections_Through_Model.objects.create(
                section_order=section_order,
                section=sec,
                order=order_idx,
            )
            order_idx += 1

        # Attach plugins
        for pentry in plugins:
            pl = None
            # Accept dict with id or name, or raw id/name
            if isinstance(pentry, dict):
                raw_pid = pentry.get("id")
                raw_pname = pentry.get("name")
            else:
                raw_pid = pentry
                raw_pname = None

            # Try integer ID first
            pk_int = None
            try:
                # Some JSON may store IDs as strings
                if raw_pid is not None:
                    pk_int = int(raw_pid)
            except (TypeError, ValueError):
                pk_int = None

            if pk_int is not None:
                try:
                    pl = Plugin.objects.get(pk=pk_int)
                except Plugin.DoesNotExist:
                    pl = None

            # Fallback to name-based lookup
            if pl is None:
                name_try = raw_pname if raw_pname else (str(pentry) if not isinstance(pentry, dict) else None)
                if name_try:
                    try:
                        pl = Plugin.objects.get(name=name_try)
                    except Plugin.DoesNotExist:
                        pl = None

            if not pl:
                self.stdout.write(self.style.WARNING(f"Plugin not found: {pentry}; skipping"))
                continue

            section_order.plugins.add(pl)

        section_order.save()
