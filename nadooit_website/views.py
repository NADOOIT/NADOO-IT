from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, "nadooit_website/index.html", {})


def impressum(request):
    return render(request, "nadooit_website/impressum.html", {})


def datenschutz(request):
    return render(request, "nadooit_website/datenschutz.html", {})
