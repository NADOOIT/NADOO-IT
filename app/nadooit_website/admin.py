from django.contrib import admin
from ordered_model.admin import OrderedTabularInline, OrderedInlineModelAdminMixin
from django.forms import ModelChoiceField
from django.db.models import Avg, Max, Min
from django.utils.html import format_html
from django.utils import timezone
from django.contrib import messages

from .models import *

from django.forms import ModelForm

import logging

from .tasks import transcode_video_to_mp4_task

from django.contrib.admin import SimpleListFilter

SESSION_ACTIVE_OFFSET = 100


class SessionStatusFilter(SimpleListFilter):
    title = "Session Status"
    parameter_name = "session_status"

    def lookups(self, request, model_admin):
        return (
            ("active", "Active"),
            ("inactive", "Inactive"),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        active_sessions = [
            session
            for session in queryset
            if session.session_end_time()
            > now - datetime.timedelta(seconds=SESSION_ACTIVE_OFFSET)
        ]
        if self.value() == "active":
            return queryset.filter(pk__in=[session.pk for session in active_sessions])
        elif self.value() == "inactive":
            return queryset.exclude(pk__in=[session.pk for session in active_sessions])


class SessionSignalsInline(admin.TabularInline):
    model = Session_Signal
    extra = 0
    readonly_fields = ("section", "session_signal_type", "session_signal_date")
    can_delete = False  # Prevent deletion of Session_Signals
    ordering = ("-session_signal_date",)  # Order Session_Signals by date

    def has_add_permission(self, request, obj=None):
        return False  # Prevent adding new Session_Signals through the admin interface


class SessionAdmin(admin.ModelAdmin):
    list_display = (
        "session_id",
        "session_section_order",
        "session_score",
        "group_average_score",
        "group_lowest_score",
        "group_highest_score",
        "session_status",
    )
    list_filter = (
        "session_section_order",
        "session_start_time",
        "session_duration",
        SessionStatusFilter,
    )
    readonly_fields = ("shown_sections",)
    inlines = [SessionSignalsInline]

    def group_average_score(self, obj):
        sessions = Session.objects.filter(
            session_section_order=obj.session_section_order
        )
        avg_score = sessions.aggregate(Avg("session_score"))["session_score__avg"]
        return round(avg_score, 2) if avg_score is not None else "N/A"

    group_average_score.short_description = "Group Average Score"
    group_average_score.admin_order_field = "session_section_order__session_score__avg"

    def group_lowest_score(self, obj):
        sessions = Session.objects.filter(
            session_section_order=obj.session_section_order
        )
        min_score = sessions.aggregate(Min("session_score"))["session_score__min"]
        return min_score if min_score is not None else "N/A"

    group_lowest_score.short_description = "Group Lowest Score"
    group_lowest_score.admin_order_field = "session_section_order__session_score__min"

    def group_highest_score(self, obj):
        sessions = Session.objects.filter(
            session_section_order=obj.session_section_order
        )
        max_score = sessions.aggregate(Max("session_score"))["session_score__max"]
        return max_score if max_score is not None else "N/A"

    group_highest_score.short_description = "Group Highest Score"
    group_highest_score.admin_order_field = "session_section_order__session_score__max"

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "shown_sections":
            kwargs["queryset"] = Section.objects.filter(
                session__shown_sections__session_id=request.session_id
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def session_status(self, obj):
        if obj.session_end_time() > timezone.now() - datetime.timedelta(
            seconds=SESSION_ACTIVE_OFFSET
        ):
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px; border-radius: 3px;">Active</span>'
            )
        else:
            return format_html(
                '<span style="background-color: red; color: white; padding: 3px; border-radius: 3px;">Inactive</span>'
            )

    session_status.short_description = "Session Status"


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


# Add VideoAdmin for managing videos in the admin panel
class VideoAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        logger.debug("Checking if the uploaded video is an MKV file")
        if obj.video_file.name.lower().endswith(".mkv"):
            logger.info("Starting transcoding task for video ID: %s", obj.id)
            transcode_video_to_mp4_task.delay(obj.id)


# Update SectionAdmin to include video field in the form
class SectionAdmin(admin.ModelAdmin):
    list_display = ("section_id", "name", "html", "video")

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

        super().save_model(request, obj, form, change)


# Register your models here.
admin.site.register(Session, SessionAdmin)
admin.site.register(Visit)

admin.site.register(Section, SectionAdmin)

admin.site.register(Section_Order, Section_OrderAdmin)
admin.site.register(Session_Signal)
admin.site.register(Signals_Option)
admin.site.register(Category)
admin.site.register(ExperimentGroup)
admin.site.register(Plugin)

# Register the new VideoAdmin
admin.site.register(Video, VideoAdmin)
