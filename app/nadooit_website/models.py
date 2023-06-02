import datetime
import random
import string
import uuid
from django.db import models
from ordered_model.models import OrderedModel
from django.core.files.storage import default_storage
import logging
from uuid import uuid4
from django.utils.deconstruct import deconstructible
from django.core.files.storage import FileSystemStorage


@deconstructible
class RenameFileStorage(FileSystemStorage):
    def get_valid_name(self, name):
        ext = name.split(".")[-1]
        name = f"{uuid4()}.{ext}"
        return name


# Create your models here.
# create a model for someone visiting the site
# the visit holds the date and time of the visit and the site the visitor visited
class Visit(models.Model):
    # the date and time of the visit
    visit_date = models.DateTimeField(auto_now_add=True)
    # the site the visitor visited
    site = models.CharField(max_length=200)

    # the string representation of the visit
    def __str__(self):
        return self.visit_date.strftime("%Y-%m-%d %H:%M:%S") + " " + self.site


class Video(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    preview_image = models.ImageField(upload_to="video_previews/")
    reprocess_video = models.BooleanField(default=False)
    original_file = models.FileField(upload_to="original_videos/")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        try:
            # is the object in the database yet?
            obj = Video.objects.get(id=self.id)
        except Video.DoesNotExist:
            # Object is not in database
            super().save(*args, **kwargs)
        else:
            # Object is in database
            # if any field has changed, delete the old file
            if (
                obj.original_file
                and obj.original_file != self.original_file
                and os.path.isfile(obj.original_file.path)
            ):
                os.remove(obj.original_file.path)

            # do the same for the preview image
            if (
                obj.preview_image
                and obj.preview_image != self.preview_image
                and os.path.isfile(obj.preview_image.path)
            ):
                os.remove(obj.preview_image.path)

            super().save(*args, **kwargs)

        if self.original_file:  # After save, the file exists
            old_file_path = self.original_file.path
            new_file_name = f"{self.id}.mp4"
            new_file_dir = os.path.dirname(old_file_path)
            new_file_path = os.path.join(new_file_dir, new_file_name)

            if os.path.exists(old_file_path):
                os.rename(old_file_path, new_file_path)
                self.original_file.name = os.path.join(
                    os.path.basename(new_file_dir), new_file_name
                )

        # do the same for the preview image
        if self.preview_image:
            old_image_path = self.preview_image.path
            old_image_extension = os.path.splitext(old_image_path)[
                1
            ]  # Get the image extension
            new_image_name = f"{self.id}{old_image_extension}"  # Use the old image extension for the new image name
            new_image_dir = os.path.dirname(old_image_path)
            new_image_path = os.path.join(new_image_dir, new_image_name)

            if os.path.exists(old_image_path):
                os.rename(old_image_path, new_image_path)
                self.preview_image.name = os.path.join(
                    os.path.basename(new_image_dir), new_image_name
                )

        super().save(
            *args, **kwargs
        )  # Save again to update the filenames in the database


from django.core.files.base import ContentFile
import os
from django.core.exceptions import ValidationError
import re

import os
import os
import shutil
from django.conf import settings

def hls_upload_to(instance, filename):
    path = f"hls_playlists/{instance.video.id}_{instance.resolution}p"
    full_path = os.path.join(settings.MEDIA_ROOT, path)

    # If the directory already exists, remove it and all its contents
    if os.path.exists(full_path):
        shutil.rmtree(full_path)

    # Now create the directory (which might have been deleted in the previous step)
    os.makedirs(full_path)

    return os.path.join(path, filename)


class VideoResolution(models.Model):
    video = models.ForeignKey(
        Video, related_name="resolutions", on_delete=models.CASCADE
    )
    resolution = models.PositiveIntegerField()
    video_file = models.FileField(upload_to="videos/")
    hls_playlist_file = models.FileField(upload_to=hls_upload_to)

    def __str__(self):
        return f"{self.video.title} ({self.resolution}p)"

    def save(self, *args, **kwargs):
        try:
            # is the object in the database yet?
            obj = VideoResolution.objects.get(id=self.id)
        except VideoResolution.DoesNotExist:
            # Object is not in database
            super().save(*args, **kwargs)
        else:
            # Object is in database
            # if any field has changed, delete the old file
            if (
                obj.video_file
                and obj.video_file != self.video_file
                and os.path.isfile(obj.video_file.path)
            ):
                os.remove(obj.video_file.path)

            super().save(*args, **kwargs)

        if self.video_file:  # After save, the file exists
            old_file_path = self.video_file.path
            new_file_name = f"{self.video.id}_{self.resolution}p.mp4"
            new_file_dir = os.path.dirname(old_file_path)
            new_file_path = os.path.join(new_file_dir, new_file_name)

            if os.path.exists(old_file_path):
                os.rename(old_file_path, new_file_path)
                self.video_file.name = os.path.join(
                    os.path.basename(new_file_dir), new_file_name
                )

        super().save(
            *args, **kwargs
        )  # Save again to update the filename in the database


class Signals_Option(models.Model):
    signal_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    signal_date = models.DateTimeField(auto_now_add=True)
    signal_type = models.CharField(max_length=200)

    def __str__(self):
        return self.signal_type


class Category(models.Model):
    name = models.CharField(
        max_length=255,
        choices=(
            ("fast_and_engaged", "Fast and Engaged"),
            ("fast_and_not_engaged", "Fast and Not Engaged"),
            ("slow_and_engaged", "Slow and Engaged"),
            ("slow_and_not_engaged", "Slow and Not Engaged"),
        ),
        unique=True,
    )

    def __str__(self):
        return self.name


class File(models.Model):
    """
    This class represents a file that can be linked to a section.
    """

    file_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    file = models.FileField(
        upload_to="uploads/"
    )  # assuming files are stored in a directory named 'uploads' at the media root

    def __str__(self):
        return self.name


# Section is a class that stores the html code of a section
class Section(models.Model):
    section_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)

    # content for the section
    html = models.TextField()
    # Add a ForeignKey to Video model with null and blank values set to True
    video = models.ForeignKey(Video, on_delete=models.SET_NULL, null=True, blank=True)

    file = models.ForeignKey(File, on_delete=models.SET_NULL, null=True, blank=True)

    categories = models.ManyToManyField(Category)

    # Classify the section as a greeting section or not
    greeting_sction = models.BooleanField(default=False)

    signal_options = models.ManyToManyField(Signals_Option, blank=True)

    def is_valid_filename(self, filename):
        return all(c.isalnum() or c in "._- " for c in filename)

    def get_valid_filename(self, filename):
        return "".join(c for c in filename if c.isalnum() or c in "._- ")

    def save(self, *args, **kwargs):
        if not self.is_valid_filename(self.name):
            self.name = self.get_valid_filename(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Plugin(models.Model):
    name = models.CharField(max_length=200)
    html = models.TextField()

    def __str__(self):
        return self.name

    def is_valid_filename(self, filename):
        return all(c.isalnum() or c in "._- " for c in filename)

    def get_valid_filename(self, filename):
        return "".join(c for c in filename if c.isalnum() or c in "._- ")

    def save(self, *args, **kwargs):
        if not self.is_valid_filename(self.name):
            self.name = self.get_valid_filename(self.name)
        super().save(*args, **kwargs)


class SectionScore(models.Model):
    section = models.OneToOneField(Section, on_delete=models.CASCADE)
    score = models.FloatField(default=0)
    experiment_group = models.IntegerField(
        choices=((0, "Control"), (1, "Experimental")), default=0
    )

    def __str__(self):
        return f"{self.section} - {self.experiment_group} - Score: {self.score}"


# Section_Order is a class that stores the order in which the sections are displayed to the visitor
# It contains a list of section ids in the order they are displayed to the visitor
# Has the visitor seen all the sections in the order a new order is generated based on the order of the sections the visitor has seen
# This means that at the beginning all Section_Order objects will have only one section in the order
# As the visitor finishes the section a new Section_Order object is created with a new section added to the order
# So over time the Section_Order objects will have more and more sections in the order
class Section_Order(models.Model):
    section_order_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    section_order_date = models.DateTimeField(auto_now_add=True)

    # section_order is a list of section ids in the order they are displayed to the visitor
    sections = models.ManyToManyField(
        Section, through="Section_Order_Sections_Through_Model"
    )

    plugins = models.ManyToManyField(Plugin)


class Section_Order_Sections_Through_Model(OrderedModel):
    section_order = models.ForeignKey(Section_Order, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    order_with_respect_to = "section_order"

    class Meta:
        ordering = ("section_order", "order")


class ExperimentGroup(models.Model):
    name = models.CharField(max_length=255)
    section_order = models.ForeignKey(
        Section_Order, on_delete=models.CASCADE, null=True
    )
    successful_sessions = models.IntegerField(default=0)
    total_sessions = models.IntegerField(default=0)

    def success_ratio(self):
        if self.total_sessions == 0:
            return 0
        return self.successful_sessions / self.total_sessions

    def __str__(self):
        return self.name


class Session(models.Model):
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    session_section_order = models.ForeignKey(Section_Order, on_delete=models.CASCADE)

    session_start_time = models.DateTimeField(auto_now_add=True)
    session_duration = models.IntegerField(default=0)
    total_interaction_time = models.FloatField(default=0)
    shown_sections = models.ManyToManyField(Section, blank=True)
    session_clicked_on_appointment_form = models.BooleanField(default=False)

    session_score = models.IntegerField(default=0)

    is_bot_visit = models.BooleanField(default=False)

    experiment_group = models.ForeignKey(
        ExperimentGroup, on_delete=models.CASCADE, null=True, blank=True
    )

    category = models.CharField(
        max_length=255, choices=(("fast", "Fast"), ("slow", "Slow")), default="fast"
    )

    variant = models.CharField(
        max_length=255,
        choices=(("control", "Control"), ("experimental", "Experimental")),
        default="control",
    )

    def session_end_time(self):
        return self.session_start_time + datetime.timedelta(
            seconds=self.session_duration
        )

    def __str__(self):
        return (
            str(self.session_id)
            + " "
            + str(self.session_duration)
            + " "
            + str(self.session_score)
            + " "
            + str(self.session_clicked_on_appointment_form)
        )

    class Meta:
        ordering = ["-session_start_time"]


class Session_Signal(models.Model):
    session_signal_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    session_signal_date = models.DateTimeField(auto_now_add=True)
    session_signal_type = models.CharField(max_length=200)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)

    session = models.ForeignKey(Session, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.section) + " " + self.session_signal_type


# Section
"""     
    Section
    section_id a unique id for the section
    name a name generated from the section to be displayed
    html the html code of the section
"""


# Section_Transition Test
"""
This model is used to store the test results for a section transition test
Each section transition Test consists of 2 sections
It stores the order of the ids of the the first section the visitor sees and the second section the visitor sees
It is to keep track how likely the visitor will continue to the next section after seeing the first section

    section_test_id
    section_test_date
    sectoin_test_time
    section_1_id
    section_2_id
    transition_percentage
"""


class Section_Transition(models.Model):
    section_transition_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    section_1_id = models.UUIDField()
    section_2_id = models.UUIDField()
    transition_percentage = models.IntegerField()

    def __str__(self):
        return (
            self.section_transition_id
            + " "
            + self.section_1_id
            + " "
            + self.section_2_id
            + " "
            + str(self.transition_percentage)
        )


class Section_Transition_Test(models.Model):
    section_test_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    section_test_date = models.DateTimeField(auto_now_add=True)
    # section_transition_id is the id of the section transition that is being tested
    section_transition_id = models.ForeignKey(
        Section_Transition, on_delete=models.CASCADE
    )

    section_was_pased = models.BooleanField(default=False)

    def __str__(self):
        return (
            self.section_test_id
            + " "
            + self.section_test_date.strftime("%Y-%m-%d %H:%M:%S")
            + " "
            + self.section_1_id
            + " "
            + self.section_2_id
            + " "
            + str(self.section_was_pased)
        )


# Each Section_Competition is a competition between 5 Section_Transition_Test
# It always sets section_1 as the same and section_2 as something diffrent.


class Section_Competition(models.Model):
    section_competition_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    section_competition_date = models.DateTimeField(auto_now_add=True)

    section_1_id = models.ForeignKey(Section, on_delete=models.CASCADE)

    section_transition_tests = models.ManyToManyField(Section_Transition_Test)

    def __str__(self):
        return (
            self.section_competition_id
            + " "
            + self.section_competition_date.strftime("%Y-%m-%d %H:%M:%S")
        )
