from django.contrib import admin

from ordered_model.admin import OrderedTabularInline, OrderedInlineModelAdminMixin
from django.forms import ModelChoiceField
from django.contrib import messages

from nadooit_website.models import *

import logging


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "file",
    )


class WebsiteSectionsOrderTabularInline(OrderedTabularInline):
    model = Section_Order_Sections_Through_Model
    fields = ("section", "move_up_down_links")
    readonly_fields = (
        "order",
        "move_up_down_links",
    )
    ordering = ("order",)
    extra = 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "section":
            kwargs["queryset"] = Section.objects.order_by("name")
            kwargs["form_class"] = ModelChoiceField
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class Section_OrderAdmin(OrderedInlineModelAdminMixin, admin.ModelAdmin):
    list_display = ("section_order_id",)
    inlines = (WebsiteSectionsOrderTabularInline,)
    save_as = True


# Update SectionAdmin to include video field in the form
class SectionAdmin(admin.ModelAdmin):
    list_display = ("section_id", "name", "html", "video", "file")

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    def save_model(self, request, obj, form, change):
        self.logger.info("Saving section with ID: %s", obj.section_id)

        if obj.video and "{{ video }}" not in obj.html:
            messages.warning(
                request,
                "A video is selected for this section, but the {{ video }} tag is missing in the HTML. Please add the tag where you want the video to appear.",
            )
        elif not obj.video and "{{ video }}" in obj.html:
            messages.warning(
                request,
                "No video is selected for this section, but the {{ video }} tag is present in the HTML. Please either add a video or remove the tag.",
            )

        if obj.file and "{{ file }}" not in obj.html:
            messages.warning(
                request,
                "A file is selected for this section, but the {{ file }} tag is missing in the HTML. Please add the tag where you want the file download link to appear.",
            )
        elif not obj.file and "{{ file }}" in obj.html:
            messages.warning(
                request,
                "No file is selected for this section, but the {{ file }} tag is present in the HTML. Please either add a file or remove the tag.",
            )

        super().save_model(request, obj, form, change)


admin.site.register(Section, SectionAdmin)
admin.site.register(Section_Order, Section_OrderAdmin)
