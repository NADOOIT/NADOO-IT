from django.http import HttpResponse


from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["POST"])
def telegram_webhook(request, secret_url):
    print("telegram_webhook")

    print("secret_url: ", secret_url)
    print("request: ", request)

    # return Status 200
    return HttpResponse(status=200)
