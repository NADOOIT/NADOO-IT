from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request, "nadooit_website/index.html", {"page_title": "Home"})


def impressum(request):
    return render(
        request, "nadooit_website/impressum.html", {"page_title": "Impressum"}
    )


def datenschutz(request):
    return render(
        request,
        "nadooit_website/datenschutz.html",
        {"page_title": "Datenschutzerklärung"},
    )
