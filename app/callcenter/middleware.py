from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from callcenter.models import MeetingRequest


class MeetingRequestNotificationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        new_requests = MeetingRequest.objects.filter(status="pending").count()
        if new_requests:
            messages.info(
                request,
                f"You have {new_requests} new meeting request(s). Refresh the page to view them.",
            )
