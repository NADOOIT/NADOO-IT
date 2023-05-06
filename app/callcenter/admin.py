from django.contrib import admin
from django.utils.html import format_html

# Register your models here.
from django.contrib import admin
from .models import MeetingRequest


from django.contrib import admin
from .models import MeetingRequest


class MeetingRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "session",
        "status",
    )
    list_filter = ("status",)
    search_fields = ("id", "session__session_id", "call_center_worker__user__username")

    actions = ["accept_request", "deny_request"]

    def accept_request(self, request, queryset):
        updated = queryset.update(status="accepted")
        self.message_user(request, f"{updated} meeting request(s) accepted.")

    def deny_request(self, request, queryset):
        updated = queryset.update(status="denied")
        self.message_user(request, f"{updated} meeting request(s) denied.")

    accept_request.short_description = "Accept selected meeting requests"
    deny_request.short_description = "Deny selected meeting requests"

    def session_status(self, obj):
        if obj.session:
            status = obj.session.session_status()
            if status == "ACTIVE":
                return format_html(
                    '<span style="background-color: green; color: white; padding: 3px; border-radius: 3px;">Active</span>'
                )
            else:
                return format_html(
                    '<span style="background-color: red; color: white; padding: 3px; border-radius: 3px;">Expired</span>'
                )
        else:
            return format_html(
                '<span style="background-color: red; color: white; padding: 3px; border-radius: 3px;">Expired</span>'
            )


admin.site.register(MeetingRequest, MeetingRequestAdmin)
