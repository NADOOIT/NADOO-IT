from django import forms
from django.contrib import admin

from nadooit_website.models import *

import logging

from nadooit_website.tasks import create_streaming_files_task
from django.conf import settings
from nadooit_website.services import delete_video_files


class VideoResolutionInline(admin.TabularInline):
    model = VideoResolution
    extra = 0


# Add VideoAdmin for managing videos in the admin panel
import os
import shutil

import os
import shutil
from django.conf import settings


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = "__all__"

    def delete_video_files(self, video):
        delete_video_files(video)
        VideoResolution.objects.filter(video=video).delete()

    def clean(self):
        cleaned_data = super().clean()

        # If the video instance already exists and a new file has been uploaded
        if self.instance.pk and "original_file" in self.changed_data:
            # Delete the old video files
            self.delete_video_files(self.instance)

        return cleaned_data


class VideoAdmin(admin.ModelAdmin):
    inlines = [VideoResolutionInline]
    form = VideoForm  # use the custom form

    actions = ["delete_associated_files"]

    def delete_associated_files(self, request, queryset):
        for video in queryset:
            delete_video_files(video)
        self.message_user(
            request,
            f"Selected video files have been deleted.{video.original_file.name}",
        )

    delete_associated_files.short_description = "Delete associated video files"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        logger.info("Starting transcoding task for video ID: %s", obj.id)
        create_streaming_files_task.delay(obj.id)


# Register the new VideoAdmin
admin.site.register(Video, VideoAdmin)
