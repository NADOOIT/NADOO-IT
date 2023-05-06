from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import MeetingRequest


@admin.register(MeetingRequest)
class MeetingRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "status", "requested_at", "worker")
    list_filter = ("status",)
    actions = ["create_meeting"]

    def create_meeting(self, request, queryset):
        # Implement the logic to create a Jitsi meeting here
        pass

    create_meeting.short_description = "Create Meeting for selected requests"
