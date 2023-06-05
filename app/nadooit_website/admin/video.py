import json
from django import forms
from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect, render
from django.core.files import File
from django.contrib import messages

from django.http import StreamingHttpResponse
from nadooit_website.services import zip_directories_and_files
from nadooit_website.tasks.video import cleanup_video_files
from nadooit_website.models import *

import logging
from django.http import FileResponse, HttpResponseRedirect

from nadooit_website.tasks import create_streaming_files_task
from django.conf import settings
from nadooit_website.services import delete_video_files, zip_files

from django.core.exceptions import ObjectDoesNotExist
from zipfile import ZipFile
import tempfile
import shutil


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
        try:
            delete_video_files(video)
            VideoResolution.objects.filter(video=video).delete()
        except ObjectDoesNotExist:
            pass

    def clean(self):
        cleaned_data = super().clean()
        for field, errors in self.errors.items():
            print(f"Field: {field}, Errors: {errors}")

        if self.instance.pk and "original_file" in self.changed_data:
            self.delete_video_files(self.instance)

            # Refresh the instance from the database
            try:
                self.instance.refresh_from_db()
            except ObjectDoesNotExist:
                pass

        return cleaned_data


import os
import json
from django.http import StreamingHttpResponse
from django.conf import settings


class VideoAdmin(admin.ModelAdmin):
    inlines = [VideoResolutionInline]
    form = VideoForm  # use the custom form

    actions = ["delete_associated_files", "export_files", "cleanup_files"]

    def cleanup_files(self, request, queryset):
        cleanup_video_files.delay()

    def export_files(self, request, queryset):
        def file_iterator(file_name, chunk_size=512):
            with open(file_name, "rb") as f:
                while True:
                    c = f.read(chunk_size)
                    if c:
                        yield c
                    else:
                        break
            os.remove(file_name)  # delete the file after serving

        for video in queryset:
            # Get file paths for the video files
            video_files = [
                os.path.join(settings.MEDIA_ROOT, f.video_file.name)
                for f in video.resolutions.all()
            ]

            # Get HLS directories
            hls_dirs = [
                os.path.dirname(
                    os.path.join(settings.MEDIA_ROOT, f.hls_playlist_file.name)
                )
                for f in video.resolutions.all()
            ]

            # Get file paths for the original video and the preview image
            original_video_file = os.path.join(
                settings.MEDIA_ROOT, video.original_file.name
            )
            preview_image_file = os.path.join(
                settings.MEDIA_ROOT, video.preview_image.name
            )

            json_path = f"{video.title}_data.json"
            # Create a JSON file with video data
            video_data = {
                "id": str(video.id),
                "title": video.title,
                "preview_image": video.preview_image.url,
                "original_file": video.original_file.url,
                "resolutions": [
                    {
                        "id": str(resolution.id),
                        "resolution": resolution.resolution,
                        "video_file": resolution.video_file.url,
                        "hls_playlist_file": resolution.hls_playlist_file.url,
                    }
                    for resolution in video.resolutions.all()
                ],
            }
            with open(json_path, "w") as json_file:
                json.dump(video_data, json_file)

            # Create a zip file with these files and directories
            zip_path = zip_directories_and_files(
                video_files
                + [json_path, original_video_file, preview_image_file]
                + hls_dirs,
                f"{video.title}_files.zip",
            )
            os.remove(json_path)

            # Return a StreamingHttpResponse that reads the file and deletes it after serving
            response = StreamingHttpResponse(file_iterator(zip_path))
            response[
                "Content-Disposition"
            ] = f'attachment; filename="{video.title}_files.zip"'
            return response

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

        # Check if the reprocess_video field is checked or if the resolutions don't exist
        if obj.reprocess_video:
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.DEBUG)

            logger.info("Starting transcoding task for video ID: %s", obj.id)
            create_streaming_files_task.delay(obj.id)

        # Reset the reprocess_video field
        obj.reprocess_video = False
        obj.save()


# Register the new VideoAdmin
admin.site.register(Video, VideoAdmin)
