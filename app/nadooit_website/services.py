import os
import random
import re
import shutil
import uuid
from typing import Optional
from django.conf import settings

from django.template import Template
from .models import (
    ExperimentGroup,
    Section_Order,
    Section_Transition,
    Session,
    Section,
    Session_Signal,
    SectionScore,
)

from django.template.loader import render_to_string


import logging

logger = logging.getLogger(__name__)

session_tick = 5


"""
# optimatzion
from . import embeddings
from sklearn.metrics.pairwise import cosine_similarity
from . import load_embeddings


def refresh_embeddings():
    load_embeddings()


def get_embedding_for_signal(signal_id):
    return embeddings[signal_id]


def get_similarity(signal_id1, signal_id2):
    embedding1 = get_embedding_for_signal(signal_id1)
    embedding2 = get_embedding_for_signal(signal_id2)
    return cosine_similarity([embedding1], [embedding2])[0][0]
 """


def get__session_tick():
    return session_tick


def add__signal(html_of_section, session_id, section_id, signal_type):
    if signal_type == "end_of_session_sections":
        logger.info(html_of_section)
        end_of_session_tracking = (
            '<div class="banner" hx-post="{% url \'nadooit_website:end_of_session_sections\' '
            + "'"
            + str(session_id)
            + "'"
            + " "
            + "'"
            + str(section_id)
            + "'"
            # replace spaces with underscores
            + ' %}" hx-swap="outerHTML" hx-trigger="revealed"'
            + 'hx-target="#end_of_session"'
            + ">"
        )
        closing_div = "</div><div id='end_of_session'>"
        return end_of_session_tracking + html_of_section + closing_div
    elif signal_type == "click":
        script = f"""
        <script>
        (function(sessionId, sectionId) {{

            document.querySelector('.section[data-session-id="' + sessionId + '"][data-section-id="' + sectionId + '"]').addEventListener('click', function() {{

                // Send the click signal
                fetch('/signal/' + sessionId + '/' + sectionId + '/click/', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }},
                    body: JSON.stringify({{}})
                }});
            }});
        }})('{session_id}', '{section_id}');
        </script>
        """
        revealed_tracking = f'<div class="section" data-session-id="{session_id}" data-section-id="{section_id}"'
        closing_div = "</div>"
        return revealed_tracking + html_of_section + closing_div + script

    elif signal_type == "mouseleave":
        script = f"""
        <script>
        (function(sessionId, sectionId) {{
            let enterTime = 0;

            document.querySelector('.section[data-session-id="' + sessionId + '"][data-section-id="' + sectionId + '"]').addEventListener('mouseenter', function() {{
                enterTime = new Date().getTime();
            }});

            document.querySelector('.section[data-session-id="' + sessionId + '"][data-section-id="' + sectionId + '"]').addEventListener('mouseleave', function() {{
                const leaveTime = new Date().getTime();
                const interactionTime = (leaveTime - enterTime) / 1000;

                // Send the interactionTime along with the mouseleave signal
                fetch('/signal/' + sessionId + '/' + sectionId + '/mouseleave/', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }},
                    body: JSON.stringify({{
                        interaction_time: interactionTime
                    }})
                }});
            }});
        }})('{session_id}', '{section_id}');
        </script>
        """
        revealed_tracking = f'<div class="section" data-session-id="{session_id}" data-section-id="{section_id}"'
        closing_div = "</div>"
        return revealed_tracking + html_of_section + closing_div + script

    elif signal_type == "vote":
        style_block = """
        <style>
            .vote-svg-button:hover:not(.highlighted-upvote):not(.highlighted-downvote) svg path {
                fill: #FFC107;
            }
            .highlighted-upvote svg path {
                fill: #00b4dc;
            }
            .highlighted-downvote svg path {
                fill: #FF4F4F;
            }
        </style>
        """

        script = f"""
        {style_block}
        <script>
            function sendVoteSignal(sessionId, sectionId, voteType, buttonElement) {{
                // Clear previous highlight
                const upvoteButton = document.getElementById('upvote-button-' + sectionId);
                const downvoteButton = document.getElementById('downvote-button-' + sectionId);

                upvoteButton.classList.remove('highlighted-upvote');
                downvoteButton.classList.remove('highlighted-downvote');

                // Highlight the selected button
                if (voteType === 'upvote') {{
                    buttonElement.classList.add('highlighted-upvote');
                }} else if (voteType === 'downvote') {{
                    buttonElement.classList.add('highlighted-downvote');
                }}

                fetch(`/signal/${{sessionId}}/${{sectionId}}/${{voteType}}/`, {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }},
                }});
            }}

            // Add event listeners to the buttons
            document.getElementById('upvote-button-{section_id}').addEventListener('click', function() {{
                sendVoteSignal('{session_id}', '{section_id}', 'upvote', this);
            }});

            document.getElementById('downvote-button-{section_id}').addEventListener('click', function() {{
                sendVoteSignal('{session_id}', '{section_id}', 'downvote', this);
            }});
        </script>
        """

        upvote_icon = """
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L10.59 3.41L2 12H9V22H15V12H22L12 2Z" fill="#212121"/>
        </svg>
        """

        downvote_icon = """
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 22L13.41 20.59L22 12H15V2H9V12H2L12 22Z" fill="#212121"/>
        </svg>
        """

        upvote_button = f'<button id="upvote-button-{section_id}" class="vote-button vote-button-{section_id} vote-svg-button" data-vote-type="upvote">{upvote_icon}</button>'
        downvote_button = f'<button id="downvote-button-{section_id}" class="vote-button vote-button-{section_id} vote-svg-button" data-vote-type="downvote">{downvote_icon}</button>'

        vote_section = (
            f'<div class="vote-section">{upvote_button}{downvote_button}</div>'
        )

        # Wrap the section content and vote buttons in a container div
        container_div = (
            f'<div class="section-container">{vote_section}{html_of_section}</div>'
        )
        return container_div + script

    else:
        revealed_tracking = (
            "<div hx-post=\"{% url 'nadooit_website:signal' "
            + "'"
            + str(session_id)
            + "'"
            + " "
            + "'"
            + str(section_id)
            + "'"
            + " '"
            # replace spaces with underscores
            + signal_type.replace(" ", "_")
            + '\' %}" hx-swap="afterend" hx-trigger="'
            + signal_type
            + '">'
        )
        closing_div = "</div>"
        return revealed_tracking + html_of_section + closing_div


def get__template__for__section(section):
    pass


def get_seen_sections(session_id):
    try:
        session = Session.objects.get(session_id=session_id)
        seen_sections = session.shown_sections.all()
        return seen_sections
    except Session.DoesNotExist:
        # Handle the case when the session does not exist
        return None


def categorize_user(session_id):
    SOME_THRESHOLD = 5

    session = Session.objects.get(session_id=session_id)
    total_interaction_time = session.total_interaction_time
    total_score = session.session_score
    shown_sections_count = session.shown_sections.count()

    if shown_sections_count > 0:
        avg_interaction_time = total_interaction_time / shown_sections_count
    else:
        avg_interaction_time = 0

    if avg_interaction_time < SOME_THRESHOLD:
        user_category = "fast"
    else:
        user_category = "slow"

    if user_category == "fast":
        if total_interaction_time >= 300 or total_score >= 50:
            user_category = "fast_and_engaged"
        else:
            user_category = "fast_and_not_engaged"
    elif user_category == "slow":
        if total_interaction_time >= 300 or total_score >= 50:
            user_category = "slow_and_engaged"
        else:
            user_category = "slow_and_not_engaged"

    logger.info(f"User category: {user_category}")

    return user_category


import uuid
from django.template.loader import render_to_string


def generate_video_embed_code(playlist_url_480p, playlist_url_720p, playlist_url_1080p):
    player_uuid = str(uuid.uuid4())
    context = {
        "player_uuid": player_uuid,
        "playlist_url_480p": playlist_url_480p,
        "playlist_url_720p": playlist_url_720p,
        "playlist_url_1080p": playlist_url_1080p,
    }

    video_embed_code = render_to_string("nadooit_website/video_embed.html", context)

    return video_embed_code


def process_video(section: Section, html_of_section: str):
    """
    This function replaces the video tag in the HTML with the appropriate video embed code.
    """
    if section.video:
        playlist_files_exist = all(
            section.video.resolutions.filter(resolution=res).first()
            and section.video.resolutions.filter(resolution=res)
            .first()
            .hls_playlist_file
            is not None
            for res in [480, 720, 1080]
        )

        if playlist_files_exist:
            video_480p_resolution = section.video.resolutions.get(resolution=480)
            playlist_url_480p = video_480p_resolution.hls_playlist_file.url

            video_720p_resolution = section.video.resolutions.get(resolution=720)
            playlist_url_720p = video_720p_resolution.hls_playlist_file.url

            video_1080p_resolution = section.video.resolutions.get(resolution=1080)
            playlist_url_1080p = video_1080p_resolution.hls_playlist_file.url

            video_embed_code = generate_video_embed_code(
                playlist_url_480p, playlist_url_720p, playlist_url_1080p
            )

            html_of_section = html_of_section.replace("{{ video }}", video_embed_code)
        else:
            logger.warning(
                f"Not all HLS playlist files exist for video {section.video.id}. Omitting video from section."
            )
            html_of_section = html_of_section.replace("{{ video }}", "")
    else:
        html_of_section = html_of_section.replace("{{ video }}", "")
        logger.warning(
            f"No video associated with the section, but {{ video }} tag is present in the HTML"
        )
    return html_of_section


def process_file(section: Section, html_of_section: str):
    """
    This function replaces the file tag in the HTML with the appropriate download button.
    """
    if "{{ file }}" in html_of_section:
        if section.file:
            file_name = section.file.name
            file_url = section.file.file.url

            # Render the file download button
            context = {"file_url": file_url, "file_name": file_name}
            file_embed_code = render_to_string(
                "nadooit_website/file_download_button.html", context
            )

            html_of_section = html_of_section.replace("{{ file }}", file_embed_code)
        else:
            html_of_section = html_of_section.replace("{{ file }}", "")
            logger.warning(
                f"No file associated with the section, but {{ file }} tag is present in the HTML"
            )
    elif section.file:
        logger.warning(
            f"A file is associated with the section, but the {{ file }} tag is missing in the HTML"
        )
    return html_of_section


def get__section_html_including_signals__for__section_and_session_id(
    section: Section, session_id
):
    html_of_section = section.html

    logger.info(f"Section: {section.html}")

    section_id = section.section_id

    signal_options = section.signal_options.all()

    if signal_options is not None:
        for signal_option in signal_options:
            html_of_section = add__signal(
                html_of_section, session_id, section_id, signal_option.signal_type
            )

    if "{{ video }}" in html_of_section:
        html_of_section = process_video(section, html_of_section)

    if "{{ file }}" in html_of_section:
        html_of_section = process_file(section, html_of_section)

    logger.info(f"Section: {html_of_section}")

    return html_of_section


def get__template__for__session_id(session_id):
    # start_section = get_next_section(session_id)

    section_entry = get__sections__for__session_id(session_id)

    # combine all the html of the sections into one html string as section_entry_html
    # use a for loop to iterate over all the sections
    # add all the tracking signals to the html

    section_entry_html = ""
    section_id = ""

    for i, section in enumerate(section_entry):
        section_id = section.section_id

        html_of_section = (
            get__section_html_including_signals__for__section_and_session_id(
                section, session_id
            )
        )

        if i == len(section_entry) - 1:
            html_of_section = add__signal(
                html_of_section, session_id, section_id, "end_of_session_sections"
            )

        section_entry_html += html_of_section

    # Addin Plugins
    plugins = Session.objects.get(
        session_id=session_id
    ).session_section_order.plugins.all()

    for i, plugin in enumerate(plugins):
        section_entry_html += plugin.html

    return Template(section_entry_html)


# Update the create__session_signal__for__session_id function
def create__session_signal__for__session_id(session_id, section_id, signal_type):
    CHANGE_FOR_VOTE = 30

    session = Session.objects.get(session_id=session_id)
    section = Section.objects.get(section_id=section_id)
    session_signal = Session_Signal(
        session_signal_type=signal_type, section=section, session=session
    )
    session_signal.save()

    # Update the section score based on the signal_type
    section_score, created = SectionScore.objects.get_or_create(section=section)

    if signal_type == "mouseenter_once":
        section_score.score += 1
        session.session_score += 1

    elif signal_type == "revealed":
        section_score.score += 5
        session.session_score += 5

    elif signal_type == "click":
        section_score.score += 20
        session.session_score += 20

    elif signal_type == "end_of_session_sections":
        session.session_score += 10

    elif signal_type == "upvote":
        # Check if there's an existing downvote for this session and section
        existing_downvote = Session_Signal.objects.filter(
            session=session, section=section, session_signal_type="downvote"
        ).first()

        if existing_downvote:
            existing_downvote.delete()
            section_score.score += CHANGE_FOR_VOTE

        section_score.score += CHANGE_FOR_VOTE
        session.session_score += CHANGE_FOR_VOTE

    elif signal_type == "downvote":
        # Check if there's an existing upvote for this session and section
        existing_upvote = Session_Signal.objects.filter(
            session=session, section=section, session_signal_type="upvote"
        ).first()

        if existing_upvote:
            existing_upvote.delete()
            section_score.score -= CHANGE_FOR_VOTE

        section_score.score -= CHANGE_FOR_VOTE
        session.session_score -= CHANGE_FOR_VOTE

    section_score.save()
    session.save()


from django.template.loader import render_to_string


def get__sections__for__session_id(session_id):
    return (
        Session.objects.get(session_id=session_id)
        .session_section_order.sections.all()
        .order_by("section_order_sections_through_model")
    )


def create__session():
    # session_variant = "control" if random.random() < 0.6 else "experimental"

    # for testing purposes
    session_variant = "control"

    section_order = get_most_successful_section_order()

    session = Session(session_section_order=section_order)

    session.save()  # Save the session first to create a record in the database

    session.variant = session_variant
    if session_variant == "experimental":
        assign_experiment_group(session.session_id)
    session.save()

    return session.session_id


def get_most_successful_section_order():
    # Replace this with the actual logic for finding the most successful Section_Order

    if settings.DEBUG:
        return Section_Order.objects.get(
            #section_order_id="ad508b5e-cebe-43a8-b068-dc37a4574605"
            section_order_id="4a0bd312-97c2-4336-850b-841381c0bcd8"
        )
    else:
        #TODO: Replace this with the actual logic for finding the most successful Section_Order/ any that exists
        return Section_Order.objects.get(
            section_order_id="b18429dd-8978-41cd-b286-8edd1100eb93"
        )


def received__session_still_active_signal__for__session_id(session_id):
    session = Session.objects.get(session_id=session_id)
    session.session_duration = session_tick + session.session_duration
    session.save()
    return session.session_id


def get_next_best_section_for_experimental_group(
    user_category, seen_sections, last_shown_section_id=None
):
    sections = (
        Section.objects.filter(categories__name=user_category)
        .exclude(section_id__in=seen_sections)
        .exclude(section_id=last_shown_section_id)
        .order_by("-sectionscore__score")
    )

    if sections.exists():
        return sections[0]
    else:
        # Try to get sections from other categories
        other_sections = (
            Section.objects.exclude(categories__name=user_category)
            .exclude(section_id__in=seen_sections)
            .exclude(section_id=last_shown_section_id)
            .order_by("-sectionscore__score")
        )
        if other_sections.exists():
            return other_sections[0]
        else:
            return None


def get__next_section__for__session_id_and_current_section_id(
    session_id, current_section_id
) -> Optional[Section]:
    session = Session.objects.get(session_id=session_id)
    current_section = Section.objects.get(section_id=current_section_id)

    current_section_order = session.session_section_order
    ordered_sections = current_section_order.sections.all().order_by(
        "section_order_sections_through_model__order"
    )

    seen_sections = session.shown_sections.values_list("section_id", flat=True)

    # Get user category
    user_category = categorize_user(session_id)

    if ordered_sections.filter(section_id=current_section_id).exists():
        index = list(ordered_sections).index(current_section)
        if index + 1 < len(ordered_sections):
            next_section = ordered_sections[index + 1]

            # Call the new function to get the next best section considering transitions
            next_best_section = get_next_best_section_with_transitions(
                user_category,
                seen_sections,
                current_section_id,
                next_section.section_id,
            )

            # Add the next best section to the session's shown_sections
            session.shown_sections.add(next_best_section)

            # Save the session
            session.save()

            return next_best_section

    return None


def get__next_best_section(session_id, current_section_id):
    current_section = Section.objects.get(id=current_section_id)
    session = Session.objects.get(session_id=session_id)
    experiment_group = session.experiment_group

    if session.variant == "control":
        section_scores = (
            SectionScore.objects.filter(experiment_group=experiment_group)
            .exclude(section=current_section)
            .order_by("-score")
        )

        if section_scores.exists():
            best_section = section_scores.first().section
            return render_to_string(
                "nadooit_website/section.html",
                {"section": Template(best_section.html)},
            )
    else:
        return get__next_section__for__session_id_and_current_section_id(
            session_id, current_section_id
        )

    return ""


def get_next_best_section_with_transitions(
    user_category, seen_sections, current_section_id, next_section_id
) -> Optional[Section]:
    # Get sections with the user_category and exclude plugin sections
    sections = Section.objects.filter(category=user_category)

    # Get transitions for the current section
    transitions = Section_Transition.objects.filter(section_1_id=current_section_id)

    # Exclude sections that have already been shown
    valid_transitions = transitions.exclude(section_2_id__in=seen_sections)

    # Filter transitions with sections that match the user_category
    valid_transitions = valid_transitions.filter(
        section_2_id__in=sections.values_list("section_id", flat=True)
    )

    # Order transitions by transition_percentage and get the best one
    best_transition = valid_transitions.order_by("-transition_percentage").first()

    if best_transition:
        # If the best_transition's next section is equal to the next_section_id, prioritize it
        if str(best_transition.section_2_id) == next_section_id:
            next_section = Section.objects.get(section_id=next_section_id)
        else:
            # If not, choose the best_transition's next section
            next_section = Section.objects.get(section_id=best_transition.section_2_id)
    else:
        # If there are no valid transitions, fall back to the next section in the ordered_sections
        next_section = Section.objects.get(section_id=next_section_id)

    return next_section


def get__next_section_html(session_id, current_section_id):
    session = Session.objects.get(session_id=session_id)
    current_section = Section.objects.get(section_id=current_section_id)

    current_section_order = session.session_section_order
    ordered_sections = current_section_order.sections.all().order_by(
        "section_order_sections_through_model__order"
    )

    seen_sections = session.shown_sections.values_list("section_id", flat=True)

    # Get user category
    user_category = categorize_user(session_id)

    if ordered_sections.filter(section_id=current_section_id).exists():
        index = list(ordered_sections).index(current_section)
        if index + 1 < len(ordered_sections):
            next_section = ordered_sections[index + 1]

            # Call the new function to get the next best section considering transitions
            next_best_section = get_next_best_section_with_transitions(
                user_category, seen_sections, current_section_id, next_section.id
            )

            if next_best_section:
                return render_to_string(
                    "nadooit_website/section.html",
                    {"section": Template(next_best_section.html)},
                )

    return ""


def check__session_id__is_valid(session_id: uuid):
    return Session.objects.filter(session_id=session_id).exists()


def get__first_section():
    # check if there are the last first section tests are done.
    # To find that out take all first section tests and check if they are done.
    # That can be figured out by checking if the session_end_time is futher in the past than the session start_time + session_duration + session_tick.
    # If all first section tests are done, evalualte them.
    # If not create a new competition and get the first section.
    pass


def assign_experiment_group(session_id):
    # Retrieve the session object using the session_id
    session = Session.objects.get(session_id=session_id)

    # Get all available experimental groups
    experiment_groups = ExperimentGroup.objects.all()

    # If there are existing experimental groups, randomly select one
    # Otherwise, create a new experimental group with the name "Default"
    if experiment_groups.exists():
        experiment_group = random.choice(experiment_groups)
    else:
        experiment_group = ExperimentGroup.objects.create(name="Default")

    # If the selected experimental group has no sessions, create a new Section_Order and assign it to the session
    if not experiment_group.session_set.exists():
        section_order = create_new_section_order()
        session.session_section_order = section_order

    # If there are existing sessions in the group, assign the same Section_Order as the other sessions in the group
    else:
        section_order = experiment_group.session_set.first().session_section_order
        session.session_section_order = section_order

    # Save the changes made to the session object
    session.save()


def create_new_section_order():
    # Replace this with the actual logic for creating a new Section_Order
    section_order = Section_Order.objects.create()
    section_order.save()
    return section_order


def get_next_section_based_on_variant(
    session_id, current_section_id, user_category, seen_sections, variant
):
    session = Session.objects.get(session_id=session_id)

    if variant == "experimental":
        next_section = get_next_best_section_for_experimental_group(
            user_category, seen_sections, last_shown_section_id=current_section_id
        )
    else:
        next_section = get__next_section__for__session_id_and_current_section_id(
            session_id, current_section_id
        )

    # Update seen_sections
    if next_section:
        session.shown_sections.add(next_section)
        session.save()

    return next_section


import glob
import json


def delete_video_files(video):
    try:
        # Load the JSON configuration file
        try:
            with open("video_config.json") as config_file:
                config = json.load(config_file)
        except Exception as e:
            print(f"Error loading configuration file: {e}")
            return

        original_file_name = os.path.splitext(
            os.path.basename(video.original_file.name)
        )[0]
        resolutions = [res["resolution"] for res in config["resolutions"]]
        for resolution in resolutions:
            video_path = os.path.join(
                settings.MEDIA_ROOT,
                "original_videos",
                f"{original_file_name}_{resolution}p.mp4",
            )
            hls_playlist_path = os.path.join(
                settings.MEDIA_ROOT,
                "hls_playlists",
                f"{original_file_name}_{resolution}p",
            )
            transcoded_video_path = os.path.join(
                settings.MEDIA_ROOT, "videos", f"{original_file_name}_{resolution}p.mp4"
            )

            if os.path.isfile(video_path):
                os.remove(video_path)
            if os.path.isdir(hls_playlist_path):
                shutil.rmtree(hls_playlist_path)
            if os.path.isfile(transcoded_video_path):
                os.remove(transcoded_video_path)

        # Deleting the original video file
        original_video_paths = glob.glob(
            os.path.join(
                settings.MEDIA_ROOT, "original_videos", f"{original_file_name}.*"
            )
        )
        for original_video_path in original_video_paths:
            if os.path.isfile(original_video_path):
                os.remove(original_video_path)

    except Exception as e:
        print(f"Error deleting video files: {e}")
        raise


import zipfile


def zip_files(file_paths, output_name):
    with zipfile.ZipFile(output_name, "w") as zipf:
        for file in file_paths:
            zipf.write(file)
    return output_name


import zipfile
import os


def zip_directories_and_files(paths, output_name):
    with zipfile.ZipFile(output_name, "w") as zipf:
        for path in paths:
            if os.path.isfile(path):
                zipf.write(path, arcname=os.path.basename(path))
            elif os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(
                            file_path, start=os.path.join(path, os.pardir)
                        )
                        zipf.write(file_path, arcname=arcname)
    return output_name


import os
import shutil
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile
from .models import Video, VideoResolution
from .models import hls_upload_to
import json
import zipfile

from django.conf import settings
import os

from django.db import transaction


@transaction.atomic
def handle_uploaded_file(file):
    temp_dir = os.path.join(settings.MEDIA_ROOT, "temp")
    os.makedirs(temp_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(file, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        with open(os.path.join(temp_dir, "video_data.json"), "r") as json_file:
            video_data = json.load(json_file)

        video, _ = Video.objects.update_or_create(
            id=video_data["id"],
            defaults={
                "title": video_data["title"],
                "preview_image": File(
                    open(os.path.join(temp_dir, video_data["preview_image"]), "rb"),
                    video_data["preview_image"],
                ),
                "original_file": File(
                    open(os.path.join(temp_dir, video_data["original_file"]), "rb"),
                    video_data["original_file"],
                ),
            },
        )

        for resolution_data in video_data["resolutions"]:
            resolution, _ = VideoResolution.objects.update_or_create(
                id=resolution_data["id"],
                defaults={
                    "video": video,
                    "resolution": resolution_data["resolution"],
                    "video_file": File(
                        open(
                            os.path.join(temp_dir, resolution_data["video_file"]), "rb"
                        ),
                        resolution_data["video_file"],
                    ),
                },
            )

            # Now move the HLS playlist files to the right place
            old_hls_folder_path = os.path.join(
                temp_dir, resolution_data["hls_playlist_file"]
            )
            new_hls_folder_path = os.path.join(
                settings.MEDIA_ROOT,
                "hls_playlists",
                f"{video.id}_{resolution.resolution}p",
            )
            os.makedirs(new_hls_folder_path, exist_ok=True)

            if os.path.isdir(old_hls_folder_path):
                if os.path.exists(new_hls_folder_path):
                    shutil.rmtree(new_hls_folder_path)  # delete the existing directory and all of its contents

                os.makedirs(new_hls_folder_path)  # recreate the directory

                for file_name in os.listdir(old_hls_folder_path):
                    src_file = os.path.join(old_hls_folder_path, file_name)
                    dest_file = os.path.join(new_hls_folder_path, file_name)

                    shutil.move(src_file, dest_file)  # now move should succeed


                # Find the .m3u8 file in the folder
                m3u8_files = glob.glob(os.path.join(new_hls_folder_path, "*.m3u8"))
                if m3u8_files:
                    # If found, assign its relative path to the hls_playlist_file field on the resolution
                    relative_m3u8_path = os.path.relpath(
                        m3u8_files[0], start=settings.MEDIA_ROOT
                    )
                    resolution.hls_playlist_file = relative_m3u8_path
                    resolution.save()

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        shutil.rmtree(temp_dir)
        raise  # re-throw the last exception

    else:
        # Delete the 'temp' directory and its contents
        shutil.rmtree(temp_dir)
