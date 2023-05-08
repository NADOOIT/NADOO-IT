from django.urls import include, path

from . import views

# This is where the urls are placed
# path("", views.index, name="index"),
urlpatterns = [
    path("", views.new_index, name="index"),
    path("impressum", views.impressum, name="impressum"),
    path("datenschutz", views.datenschutz, name="datenschutz"),
    path("statistics", views.statistics, name="statistics"),
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
]
"""     
    path(
        "visualize-session-data/",
        views.visualize_session_data,
        name="visualize_session_data",
    ),
"""
