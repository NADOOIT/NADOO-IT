import json
import django.http
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Question_Answer

from nadooit_website.services import check__session_id__is_valid

# Create your views here.


@csrf_exempt
@require_POST
def submit_question(request, session_id):
    data = json.loads(request.body)
    question = data.get("question")

    # Process the question and session_id here.
    # You may want to save the question to the database or perform other actions.
    if check__session_id__is_valid(session_id):

        # create a question answer object
        Question_Answer.objects.create(question_answer_question=question)
        response_data = {
            "message": "Frage eingereicht",
            "question": question,
            "session_id": session_id,
        }
        return django.http.JsonResponse(response_data)

    else:
        return django.http.HttpResponseForbidden()
