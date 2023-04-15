import random
import uuid
from typing import Optional

from django.template import Template
from .models import (
    ExperimentGroup,
    Section_Order,
    Section_Transition,
    Session,
    Section,
    Session_Signals,
    SectionScore,
)


import logging

logger = logging.getLogger(__name__)

session_tick = 5


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

    elif signal_type == "mouseleave":
        script = """
        <script>
        let enterTime = 0;

        function onMouseEnter() {
            enterTime = new Date().getTime();
        }

        function onMouseLeave(sessionId, sectionId) {
            const leaveTime = new Date().getTime();
            const interactionTime = (leaveTime - enterTime) / 1000;

            // Send the interactionTime along with the mouseleave signal
            fetch(`/signal/${sessionId}/${sectionId}/mouseleave/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    interaction_time: interactionTime
                })
            });
        }

        </script>
        """
        revealed_tracking = f'<div class="section" onmouseenter="onMouseEnter()" onmouseleave="onMouseLeave(\'{session_id}\', \'{section_id}\')">'

        closing_div = "</div>"
        return revealed_tracking + html_of_section + closing_div + script

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


def get__section_html_including_signals__for__section_and_session_id(
    section: Section, session_id
):
    html_of_section = section.section_html

    logger.info(f"Section: {section.section_html}")

    section_id = section.section_id

    signal_options = section.signal_options.all()

    if signal_options is not None:
        for signal_option in signal_options:
            html_of_section = add__signal(
                html_of_section,
                session_id,
                section_id,
                signal_option.signal_type,
            )

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

    # Add end of session signal to the last section

    return Template(section_entry_html)


# Update the create__session_signal__for__session_id function
def create__session_signal__for__session_id(session_id, section_id, signal_type):
    session = Session.objects.get(session_id=session_id)
    section = Section.objects.get(section_id=section_id)
    session_signal = Session_Signals(session_signal_type=signal_type, section=section)
    session_signal.save()
    session.session_signals.add(session_signal)

    # Update the section score based on the signal_type
    section_score, created = SectionScore.objects.get_or_create(section=section)
    if signal_type == "mouseenter_once":
        section_score.score += 1
        session.session_score += 1

    elif signal_type == "revealed":
        section_score.score += 5
        session.session_score += 5

    elif signal_type == "end_of_session_sections":
        session.session_score += 10

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
    session_variant = "control" if random.random() < 0.6 else "experimental"

    # for testing purposes
    session_variant = "experimental"

    section_order = Section_Order.objects.get(
        section_order_id="7b3064b3-8b6c-4e3e-acca-f7750e45129b"
    )
    sections = section_order.sections.all()

    session = Session(session_section_order=section_order)
    session.save()  # Save the session first to create a record in the database

    session.shown_sections.set(sections)  # Set the shown_sections attribute
    session.save()  # Save the session again to update the shown_sections attribute

    session.variant = session_variant
    if session_variant == "experimental":
        assign_experiment_group(session.session_id)
    session.save()

    return session.session_id


def received__session_still_active_signal__for__session_id(session_id):
    session = Session.objects.get(session_id=session_id)
    session.session_duration = session_tick + session.session_duration
    session.save()
    return session.session_id


def get_next_best_section_for_experimental_group(
    user_category, seen_sections, last_shown_section_id=None
):
    sections = (
        Section.objects.filter(categories__name=user_category, plugin=False)
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
            .exclude(section_id__in=seen_sections, plugin=False)
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
                {"section": Template(best_section.section_html)},
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
    sections = Section.objects.filter(category=user_category, plugin=False)

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


from django.template.loader import render_to_string


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
                    {"section": Template(next_best_section.section_html)},
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
    experiment_groups = ExperimentGroup.objects.all()
    if experiment_groups.exists():
        experiment_group = random.choice(experiment_groups)
    else:
        experiment_group = ExperimentGroup.objects.create(name="Default")
    return experiment_group


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
