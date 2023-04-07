import django.http
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .services import get__template__for__session_id
from .services import get__session_tick
from .services import (
    received__session_still_active_signal__for__session_id,
)
from .services import create__session
from .services import check__session_id__is_valid
from .services import get__next_section

from nadooit_auth.models import User
from .models import Visit


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

    if request.htmx:
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

    else:
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


def get_next_section(request, session_id):
    if request.htmx:
        if check__session_id__is_valid(session_id):

            return render(request, get__next_section(session_id))

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
