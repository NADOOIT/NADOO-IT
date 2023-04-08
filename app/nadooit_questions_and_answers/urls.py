from django.urls import path

from . import views

# This is where the urls are placed
urlpatterns = [
    path(
        "your_question_we_answer/question/<str:session_id>",
        views.submit_question,
        name="submit_question",
    ),
]
