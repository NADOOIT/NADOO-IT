import json
from django.template import Template
import django.http
from django.shortcuts import get_object_or_404, redirect, render
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
    handle_uploaded_file,
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
from .models import Section, Session, Visit, ContentPage
from .forms import ContentPageForm

from django.views.decorators.csrf import csrf_exempt

import logging
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
import os
import re

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


from django.contrib.auth.decorators import login_required


@login_required
def content_page_preview(request, slug: str):
    """Staff-only preview for unpublished and published ContentPages.
    Returns 403 for authenticated non-staff, redirects anonymous to login.
    """
    if not request.user.is_staff:
        return django.http.HttpResponseForbidden()
    page = get_object_or_404(ContentPage, slug=slug)
    return render(
        request,
        "nadooit_website/content_page.html",
        {
            "page": page,
            "page_title": page.title,
        },
    )


@login_required
def manage_content_pages(request):
    """List ContentPages for users with view/change/add permission."""
    if not (
        request.user.has_perm("nadooit_website.view_contentpage")
        or request.user.has_perm("nadooit_website.change_contentpage")
        or request.user.has_perm("nadooit_website.add_contentpage")
    ):
        return django.http.HttpResponseForbidden()
    pages = ContentPage.objects.all().order_by("-updated_at")
    return render(
        request,
        "nadooit_website/content_page_list.html",
        {"pages": pages, "page_title": "Manage pages"},
    )


@login_required
def manage_content_page_new(request):
    """Create a new ContentPage. Requires add_contentpage permission."""
    if not request.user.has_perm("nadooit_website.add_contentpage"):
        return django.http.HttpResponseForbidden()
    if request.method == "POST":
        form = ContentPageForm(request.POST)
        if form.is_valid():
            page = form.save()
            return redirect("nadooit_website:content_page", page.slug)
    else:
        form = ContentPageForm()
    return render(
        request,
        "nadooit_website/content_page_form.html",
        {"form": form, "page_title": "New page"},
    )


@login_required
def manage_content_page_edit(request, slug: str):
    """Edit an existing ContentPage. Requires change_contentpage permission."""
    if not request.user.has_perm("nadooit_website.change_contentpage"):
        return django.http.HttpResponseForbidden()
    page = get_object_or_404(ContentPage, slug=slug)
    if request.method == "POST":
        form = ContentPageForm(request.POST, instance=page)
        if form.is_valid():
            form.save()
            return redirect("nadooit_website:content_page", page.slug)
    else:
        form = ContentPageForm(instance=page)
    return render(
        request,
        "nadooit_website/content_page_form.html",
        {"form": form, "page_title": f"Edit: {page.title}"},
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


def content_page(request, slug: str):
    """Render a simple content page composed from stored HTML and optional CSS.
    Only published content is accessible.
    """
    page = get_object_or_404(ContentPage, slug=slug, is_published=True)
    return render(
        request,
        "nadooit_website/content_page.html",
        {
            "page": page,
            "page_title": page.title,
        },
    )


@csrf_exempt
def end_of_session_sections(request, session_id, current_section_id):
    if getattr(request, "htmx", False):
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
    if getattr(request, "htmx", False):
        if check__session_id__is_valid(session_id):
            next_section_html = get__next_section_html(session_id, current_section_id)
            if next_section_html:
                # Render the standard wrapper and include the section HTML as a Template,
                # mirroring the pattern used in end_of_session_sections
                return render(
                    request,
                    "nadooit_website/section.html",
                    {"section_entry": Template(next_section_html)},
                )
            else:
                return django.http.HttpResponse("No more sections available.")
        else:
            return django.http.HttpResponseForbidden()
    else:
        return django.http.HttpResponseForbidden()


@csrf_exempt
def session_is_active_signal(request, session_id):
    if getattr(request, "htmx", False):
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
    # Allow group_filter via query param or URL kwarg, sanitized to a slug
    raw_filter = request.GET.get("group_filter") or group_filter
    group = raw_filter if raw_filter and re.fullmatch(r"[A-Za-z0-9_-]+", str(raw_filter)) else None

    # Safe file resolution to satisfy CodeQL and prevent traversal
    from pathlib import Path
    import os as _os

    base_dir = Path(settings.BASE_DIR) / "nadooit_website" / "section_transition"
    base_resolved = base_dir.resolve()

    # Build an allowlist of permissible template files
    allowed_names = {"section_transitions.html"}
    allowed_names.update({p.name for p in base_resolved.glob("section_transitions_*.html")})

    if group:
        requested = f"section_transitions_{group}.html"
        if requested not in allowed_names:
            return HttpResponse(status=404)
        chosen_name = requested
    else:
        chosen_name = "section_transitions.html"

    candidate = (base_resolved / chosen_name).resolve()

    # Ensure candidate is within base_dir
    try:
        candidate.relative_to(base_resolved)
    except ValueError:
        return HttpResponse(status=404)

    if not candidate.is_file():
        return HttpResponse(status=404)

    try:
        flags = _os.O_RDONLY
        if hasattr(_os, "O_NOFOLLOW"):
            flags |= _os.O_NOFOLLOW
        fd = _os.open(str(candidate), flags)
        try:
            with _os.fdopen(fd, "r", encoding="utf-8") as file:
                content = file.read()
        except Exception:
            _os.close(fd)
            raise
    except FileNotFoundError:
        return HttpResponse(status=404)

    return HttpResponse(content, content_type="text/html")


""" TODO #213 Create a methode to visulize session data
def visualize_session_data(request):
    # Call the function to generate the Plotly HTML file
    analyze_and_visualize_session_data()

    # Render the section_transitions.html template
    return render(request, "section_transitions.html")
 """

from django.shortcuts import render
from .forms import UploadZipForm


from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
@staff_member_required
def upload_video_zip(request):
    if request.method == "POST":
        form = UploadZipForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                handle_uploaded_file(request.FILES["file"])
                messages.success(
                    request, "The video zip file was successfully processed."
                )
            except Exception as e:
                messages.error(
                    request, f"Failed to process the video zip file: {str(e)}"
                )
            return redirect("admin:nadooit_website_video_changelist")
    else:
        form = UploadZipForm()
    return render(request, "nadooit_website/upload.html", {"form": form})
