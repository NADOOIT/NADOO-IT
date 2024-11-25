from django.urls import path
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

def test_view(request):
    return HttpResponse('Test View')

urlpatterns = [
    path('test/', test_view, name='test-view'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
