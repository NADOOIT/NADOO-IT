from django.urls import path

from . import views

# This is where the urls are placed
# path("", views.index, name="index"),
urlpatterns = [
    path("", views.new_index, name="index"),
    path("impressum", views.impressum, name="impressum"),
    path("datenschutz", views.datenschutz, name="datenschutz"),
    path("statistics", views.statistics, name="statistics"),
    path("pages/<slug:slug>/", views.content_page, name="content_page"),
    path("pages/preview/<slug:slug>/", views.content_page_preview, name="content_page_preview"),
    path("pages/manage/", views.manage_content_pages, name="manage_content_pages"),
    path("pages/manage/new/", views.manage_content_page_new, name="manage_content_page_new"),
    path("pages/manage/<slug:slug>/edit/", views.manage_content_page_edit, name="manage_content_page_edit"),
    path(
        "get_next_section/<str:session_id>/<str:current_section_id>",
        views.get_next_section,
        name="get_next_section",
    ),
    path(
        "end_of_session_sections/<str:session_id>/<str:current_section_id>",
        views.end_of_session_sections,
        name="end_of_session_sections",
    ),
    path(
        "signal/<uuid:session_id>/<slug:section_id>/<slug:signal_type>/",
        views.signal,
        name="signal",
    ),
    path(
        "session_is_active_signal/<str:session_id>",
        views.session_is_active_signal,
        name="session_is_active_signal",
    ),
    path("section_transitions/", views.section_transitions, name="section_transitions"),
    path(
        "section_transitions/<str:group_filter>/",
        views.section_transitions,
        name="section_transitions_filtered",
    ),
    path("upload/", views.upload_video_zip, name="video_upload"),
]
"""     
    path(
        "visualize-session-data/",
        views.visualize_session_data,
        name="visualize_session_data",
    ),
"""
