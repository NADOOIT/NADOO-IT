from celery import shared_task
from .models import (
    Session,
    Section_Order,
    Section_Order_Sections_Through_Model,
    Section,
)
from django.db.models import Count
import os


from moviepy.editor import VideoFileClip
import gzip
import shutil


def convert_to_mp4(input_path, output_path):
    clip = VideoFileClip(input_path)
    clip.write_videofile(output_path, codec="libx264")


def reduce_bitrate(input_path, output_path, target_bitrate):
    clip = VideoFileClip(input_path)
    target_bitrate = target_bitrate / 1000  # Convert target bitrate to kbps
    clip.write_videofile(output_path, codec="libx264", bitrate=f"{target_bitrate}k")


def compress_video(input_path, output_path):
    with open(input_path, "rb") as src_file:
        with gzip.open(output_path, "wb") as dest_file:
            shutil.copyfileobj(src_file, dest_file)


def process_video(input_path, output_path, target_bitrate=None):
    temp_path = os.path.splitext(input_path)[0] + "_temp.mp4"
    convert_to_mp4(input_path, temp_path)

    if target_bitrate:
        reduce_bitrate(temp_path, output_path, target_bitrate)
        os.remove(temp_path)
    else:
        os.rename(temp_path, output_path)

    compress_video(output_path, output_path + ".gz")


@shared_task
def update_session_section_order(session_id, next_section_id):
    session = Session.objects.get(session_id=session_id)
    next_section = Section.objects.get(section_id=next_section_id)

    # Get the current Section_Order of the Session
    current_section_order = session.session_section_order

    # Fetch the Section_Order_Sections_Through_Model objects for the current section order
    current_section_order_sections = (
        current_section_order.sections.through.objects.filter(
            section_order=current_section_order
        ).order_by("order")
    )
    current_section_order_sections_ids = [
        section.section_id for section in current_section_order_sections
    ]

    # Build the new section list by appending the next section
    new_section_list = current_section_order_sections_ids + [next_section_id]

    # Check if there exists an equivalent Section_Order
    equivalent_section_order = None
    for section_order in Section_Order.objects.annotate(count=Count("sections")).filter(
        count=len(new_section_list)
    ):
        sections_with_order = Section_Order_Sections_Through_Model.objects.filter(
            section_order=section_order
        ).order_by("order")
        ordered_sections = [sos.section_id for sos in sections_with_order]

        if ordered_sections == new_section_list:
            equivalent_section_order = section_order
            break

    # If such an Section_Order exists, replace the Section_Order in the Session
    if equivalent_section_order:
        session.session_section_order = equivalent_section_order
        session.save()
    else:
        # If no such Section_Order exists, create a new Section_Order with all the Sections from the old Section_Order and add the new Section to the end.
        new_section_order = Section_Order.objects.create()
        for index, section_id in enumerate(new_section_list):
            Section_Order_Sections_Through_Model.objects.create(
                section_order=new_section_order, section_id=section_id, order=index
            )
        new_section_order.save()

        session.session_section_order = new_section_order
        session.save()


@shared_task
def transcode_video_to_mp4_task(video_id):
    from django.db import connections
    from .models import (
        Video,
    )  # Import Video model inside the function to avoid circular import
    import os
    from django.core.files import File

    video = Video.objects.get(id=video_id)
    connections.close_all()  # Close the database connection after fetching the video object
    input_path = video.video_file.path
    output_path = os.path.splitext(input_path)[0] + ".mp4"

    # Replace the moviepy conversion with the process_video function
    process_video(input_path, output_path)

    with open(output_path, "rb") as transcoded_file:
        connections["default"].connect()  # Reopen the database connection before saving
        video.video_file.save(
            os.path.basename(output_path), File(transcoded_file), save=True
        )

    os.remove(input_path)
