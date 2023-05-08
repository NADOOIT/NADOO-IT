from django.urls import path
from . import views

urlpatterns = [
    # ... your other urlpatterns ...
    path(
        "create-meeting-request/",
        views.create_meeting_request,
        name="create_meeting_request",
    ),
]
