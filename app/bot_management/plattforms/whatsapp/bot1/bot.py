from bot_management.plattforms.whatsapp.utils import get_message_for_request
from bot_management.plattforms.whatsapp.utils import register_bot
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


@csrf_exempt
@register_bot(bot_register_id="3cfa80bb-f3c1-49ff-bf1d-2f51f5f22138")
def bot(request, *args, token=None, **kwargs):
    print(request)
    print("AND HERE")
    # HTTPS 200 OK response required
    # If get request, return challenge
    if request.method == "GET":
        challenge = request.GET.get("hub.challenge")
        if not challenge:
            return HttpResponse("Missing challenge", status=400)
        # Accept only digits to avoid reflecting HTML/JS
        if not str(challenge).isdigit():
            return HttpResponse("Invalid challenge", status=400)
        return HttpResponse(challenge, content_type="text/plain")

    # If post request, handle message
    elif request.method == "POST":
        message = get_message_for_request(request)
        print(message)

    return HttpResponse(status=200)
