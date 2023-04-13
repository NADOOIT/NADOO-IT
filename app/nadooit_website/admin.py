from django.contrib import admin
from ordered_model.admin import OrderedTabularInline, OrderedInlineModelAdminMixin
from django.forms import ModelChoiceField

from .models import *


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
            kwargs["queryset"] = Section.objects.order_by("section_name")
            kwargs["form_class"] = ModelChoiceField
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class Section_OrderAdmin(OrderedInlineModelAdminMixin, admin.ModelAdmin):
    list_display = ("section_order_id",)
    inlines = (WebsiteSectionsOrderTabularInline,)
    save_as = True


class SectionAdmin(admin.ModelAdmin):
    list_filter = ("plugin",)  # Add a filter for the 'plugin' field


# Register your models here.
admin.site.register(Visit)
admin.site.register(Session)
admin.site.register(Section, SectionAdmin)
admin.site.register(Section_Order, Section_OrderAdmin)
admin.site.register(Signals_Option)
admin.site.register(Category)
