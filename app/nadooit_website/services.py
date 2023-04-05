import uuid

from django.template import Template
from .models import Section_Order, Session, Section

session_tick = 5


def get__session_tick():
    return session_tick


def add__signal(html_of_section, session_id, section_id, signal_type):
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


def get__template__for__session_id(session_id):
    # start_section = get_next_section(session_id)

    section_entry = get__sections__for__session_id(session_id)

    # combine all the html of the sections into one html string as section_entry_html
    # use a for loop to iterate over all the sections
    # add all the tracking signals to the html

    section_entry_html = ""

    for section in section_entry:

        html_of_section = section.section_html
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

        section_entry_html += html_of_section

    return Template(section_entry_html)


def get__sections__for__session_id(session_id):
    return (
        Session.objects.get(session_id=session_id)
        .session_section_order.sections.all()
        .order_by("section_order_sections_through_model")
    )


def create__session():

    session_section_order = Section_Order.objects.get(
        section_order_id="7b3064b3-8b6c-4e3e-acca-f7750e45129b"
    )

    session = Session.objects.create(
        session_score=0, session_section_order=session_section_order
    )
    session.save()
    return session.session_id


def received__session_still_active_signal__for__session_id(session_id):
    session = Session.objects.get(session_id=session_id)
    session.session_duration = session_tick + session.session_duration
    session.save()
    return session.session_id


def get__next_section(session_id):
    # check if fist section
    if Session.objects.filter(session_id=session_id).exists():
        session = Session.objects.get(session_id=session_id)
        if session.session_score == 0:
            # get first section
            pass
        else:
            pass
            # get next section


def check__session_id__is_valid(session_id: uuid):
    return Session.objects.filter(session_id=session_id).exists()


def get__first_section():
    # check if there are the last first section tests are done.
    # To find that out take all first section tests and check if they are done.
    # That can be figured out by checking if the session_end_time is futher in the past than the session start_time + session_duration + session_tick.
    # If all first section tests are done, evalualte them.
    # If not create a new competition and get the first section.
    pass
