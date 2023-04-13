import json
from pipes import Template
import django.http
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from .services import (
    add__signal,
    categorize_user,
    create__session_signal__for__session_id,
    get__template__for__session_id,
    get_next_section_based_on_variant,
    get_seen_sections,
)
from .services import get__session_tick
from .services import (
    received__session_still_active_signal__for__session_id,
)
from .services import create__session
from .services import check__session_id__is_valid
from .services import get__next_section_html

from nadooit_auth.models import User
from .models import Section, Session, Visit

from django.template import Template, Context
from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt, csrf_protect

import logging

logger = logging.getLogger(__name__)


def user_is_staf(user: User) -> bool:
    return user.is_staff


# Create your views here.
def index(request):

    # create a visit object for the index page
    visit = Visit(site="Index")
    # save the visit
    visit.save()

    return render(request, "nadooit_website/index.html", {"page_title": "Home"})


@csrf_exempt
def signal(request, session_id, section_id, signal_type):

    if check__session_id__is_valid(session_id):

        create__session_signal__for__session_id(session_id, section_id, signal_type)

        if signal_type == "mouseenter_once":
            logger.info(
                str(session_id)
                + " "
                + str(section_id)
                + " "
                + str(signal_type)
                + " "
                + "signal received"
            )
        if signal_type == "mouseleave":

            body_unicode = request.body.decode("utf-8")
            body = json.loads(body_unicode)
            interaction_time = body.get("interaction_time", 0)
            session = Session.objects.get(session_id=session_id)
            session.total_interaction_time += float(interaction_time)
            session.save()

        if signal_type == "revealed":
            logger.info(
                str(session_id)
                + " "
                + str(section_id)
                + " "
                + str(signal_type)
                + " "
                + "signal received"
            )

            session = Session.objects.get(session_id=session_id)
            section = get_object_or_404(Section, section_id=section_id)
            session.shown_sections.add(section)
            session.save()

        if signal_type == "end_of_session_sections":
            logger.info(
                str(session_id)
                + " "
                + str(section_id)
                + " "
                + str(signal_type)
                + " "
                + "signal received"
            )

        return django.http.HttpResponse()

    else:
        return django.http.HttpResponseForbidden()


@csrf_exempt
def end_of_session_sections(request, session_id, current_section_id):
    if request.htmx:

        logger.info("end_of_session_sections htmx")

        if check__session_id__is_valid(session_id):

            logger.info("end_of_session_sections valid session")

            create__session_signal__for__session_id(
                section_id=current_section_id,
                session_id=session_id,
                signal_type="end_of_session_sections",
            )

            session = Session.objects.get(session_id=session_id)

            logger.info("end_of_session_sections session: " + str(session))

            user_category = categorize_user(session_id)

            logger.info("end_of_session_sections user_category: " + str(user_category))

            seen_sections = get_seen_sections(session_id)

            logger.info("end_of_session_sections seen_sections: " + str(seen_sections))

            logger.info(
                "end_of_session_sections session.variant: " + str(session.variant)
            )

            next_section = get_next_section_based_on_variant(
                session_id,
                current_section_id,
                user_category,
                seen_sections,
                session.variant,
            )

            logger.info("end_of_session_sections next_section: " + str(next_section))
            logger.info(next_section.section_html)

            if next_section:

                next_section_html = add__signal(
                    next_section.section_html,
                    session_id,
                    next_section.section_id,
                    "end_of_session_sections",
                )

                logger.info(
                    "end_of_session_sections next_section_html: "
                    + str(next_section_html)
                )

                # Create a temporary template from the HTML string
                # temp_template = Template(next_section_html)

                # Create a context with any necessary variables (if needed)
                # context = Context({})

                rendered_html = render(
                    request,
                    "nadooit_website/section.html",
                    {"section_entry": Template(next_section_html)},
                )

                logger.info(rendered_html)

                # Render the template with the given context
                # rendered_html = temp_template.render(context)

                # Return the rendered HTML as an HttpResponse
                return rendered_html
            else:
                return django.http.HttpResponse("No more sections available.")
        else:

            logger.info("end_of_session_sections invalid session")

            return django.http.HttpResponseForbidden()
    else:

        logger.info("end_of_session_sections forbidden")

        return django.http.HttpResponseForbidden()


def new_index(request):

    # create a visit object for the index page
    visit = Visit(site="New_Index")
    # save the visit
    visit.save()

    # create a session id used to identify the user for the visit
    session_id = create__session()

    section_entry_template = get__template__for__session_id(session_id)

    return render(
        request,
        "nadooit_website/new_index.html",
        {
            "page_title": "Home",
            "session_id": session_id,
            # "section_entry": section_entry_html,
            "section_entry": section_entry_template,
            "session_tick": get__session_tick(),
        },
    )


def get_next_section(request, session_id, current_section_id):
    if request.htmx:
        if check__session_id__is_valid(session_id):
            next_section_template = get__next_section_html(
                session_id, current_section_id
            )
            if next_section_template:
                return render(request, next_section_template)
            else:
                return django.http.HttpResponse("No more sections available.")
        else:
            return django.http.HttpResponseForbidden()
    else:
        return django.http.HttpResponseForbidden()


@csrf_exempt
def session_is_active_signal(request, session_id):
    if request.htmx:
        if check__session_id__is_valid(session_id):
            # all active sessions send a singlnal to this view
            # the time is set to session_duration of the session for the given session_id in the database

            received__session_still_active_signal__for__session_id(session_id)
            return django.http.HttpResponse()

        else:
            return django.http.HttpResponseForbidden()

    else:
        return django.http.HttpResponseForbidden()


def impressum(request):

    # create a visit object
    visit = Visit(site="Impressum")
    # save the visit
    visit.save()

    return render(
        request, "nadooit_website/impressum.html", {"page_title": "Impressum"}
    )


def datenschutz(request):

    # create a visit object
    visit = Visit(site="Datenschutz")
    # save the visit
    visit.save()

    return render(
        request,
        "nadooit_website/datenschutz.html",
        {"page_title": "Datenschutzerklärung"},
    )


@login_required(login_url="/auth/login-user")
@user_passes_test(user_is_staf, login_url="/auth/login-user")
def statistics(request):
    return render(
        request,
        "nadooit_website/statistics.html",
        {"page_title": "Statistiken", "visits": Visit.objects.all()},
    )
