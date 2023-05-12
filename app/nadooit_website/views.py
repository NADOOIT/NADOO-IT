import json
from pipes import Template
from uuid import uuid4
import django.http
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required, user_passes_test

from nadooit_website.visulize import analyze_and_visualize_session_data
from .services import (
    add__signal,
    categorize_user,
    create__session_signal__for__session_id,
    get__section_html_including_signals__for__section_and_session_id,
    get__template__for__session_id,
    get_next_section_based_on_variant,
    get_seen_sections,
)
from .tasks import update_session_section_order
from .services import get__session_tick
from .services import (
    received__session_still_active_signal__for__session_id,
)
from .services import create__session
from .services import check__session_id__is_valid
from .services import get__next_section_html

from nadooit_auth.models import User
from .models import Section, Session, Visit

from django.template import Template

from django.views.decorators.csrf import csrf_exempt

import logging
from django.http import HttpResponse
from django.conf import settings
import os

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
            if (
                body_unicode
            ):  # Add this condition to check if the request body is not empty
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
        if signal_type == "upvote":
            logger.info(
                str(session_id)
                + " "
                + str(section_id)
                + " "
                + str(signal_type)
                + " "
                + "signal received"
            )
            # Add your logic for handling upvote signals here

        if signal_type == "downvote":
            logger.info(
                str(session_id)
                + " "
                + str(section_id)
                + " "
                + str(signal_type)
                + " "
                + "signal received"
            )
            # Add your logic for handling downvote signals here

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

            if next_section:
                update_session_section_order.delay(
                    session.session_id, next_section.section_id
                )

                logger.info("getting html for the next section including signals")
                next_section_html = (
                    get__section_html_including_signals__for__section_and_session_id(
                        next_section, session_id
                    )
                )

                logger.info("Adding end_of_session_sections signal to html")
                next_section_html = add__signal(
                    next_section_html,
                    session_id,
                    next_section.section_id,
                    "end_of_session_sections",
                )

                logger.info(
                    "end_of_session_sections next_section_html: "
                    + str(next_section_html)
                )

                rendered_html = render(
                    request,
                    "nadooit_website/section.html",
                    {"section_entry": Template(next_section_html)},
                )

                logger.info(rendered_html)

                return rendered_html
            else:
                return django.http.HttpResponse("No more sections available.")
        else:
            logger.info("end_of_session_sections invalid session")

            return django.http.HttpResponseForbidden()
    else:
        logger.info("end_of_session_sections forbidden")

        return django.http.HttpResponseForbidden()


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


def section_transitions(request, group_filter=None):
    filename = (
        f"section_transitions_{group_filter}.html"
        if group_filter
        else "section_transitions.html"
    )
    file_path = os.path.join(
        settings.BASE_DIR, "nadooit_website", "section_transition", filename
    )

    with open(file_path, "r") as file:
        content = file.read()

    return HttpResponse(content, content_type="text/html")


""" TODO #213 Create a methode to visulize session data
def visualize_session_data(request):
    # Call the function to generate the Plotly HTML file
    analyze_and_visualize_session_data()

    # Render the section_transitions.html template
    return render(request, "section_transitions.html")
 """


from django.core.exceptions import MultipleObjectsReturned
from django.http import JsonResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import OnlineVideoMeetingRequest
from nadooit_website.models import Session
from django.core.exceptions import ObjectDoesNotExist


@csrf_exempt
def create_meeting_request(request):
    print("create_meeting_request")
    try:
        if request.method == "POST":
            print("POST")
            session_id = request.POST.get("session_id")
            print("session_id", session_id)
            print("request", request)
            session = Session.objects.get(pk=session_id)
            user = request.user if request.user.is_authenticated else None

            # Check if there is an active request for the session
            try:
                active_request = OnlineVideoMeetingRequest.objects.get(
                    session=session, status="pending"
                )
                print("active_request", active_request)
                return JsonResponse(
                    {
                        "status": "error",
                        "error": "An active request already exists",
                    },
                    content_type="application/json",
                )
            except OnlineVideoMeetingRequest.DoesNotExist:
                print("no active_request")
                pass  # No active request found, continue creating a new one
            except MultipleObjectsReturned:
                print("Multiple active requests found")
                return JsonResponse(
                    {
                        "status": "error",
                        "error": "Multiple active requests found",
                    },
                    content_type="application/json",
                )

            print("create_meeting_request")
            # Create a new MeetingRequest
            room_uuid = uuid4()
            # Create a new MeetingRequest
            meeting_request = OnlineVideoMeetingRequest(
                session=session, user=user, room_name=str(room_uuid)
            )
            meeting_request.save()

            print("meeting_request id", room_uuid)

            # Return a JSON response indicating success, the meeting status, and the room UUID
            return JsonResponse(
                {
                    "status": "success",
                    "meeting_status": meeting_request.status,
                    "room_uuid": str(room_uuid),
                },
                content_type="application/json",
            )

        else:
            return JsonResponse(
                {
                    "status": "error",
                    "error": "Invalid request method",
                },
                content_type="application/json",
            )

    except ObjectDoesNotExist:
        print("Session not found")
        return JsonResponse(
            {
                "status": "error",
                "error": "Session not found",
            },
            content_type="application/json",
        )

    except Exception as e:
        return JsonResponse(
            {
                "status": "error",
                "error": str(e),
            },
            content_type="application/json",
        )


@csrf_exempt
def get_meeting_request_button(request):
    try:
        if request.method == "GET":
            pass
    except Exception as e:
        pass
