from django.core.exceptions import MultipleObjectsReturned
from django.http import JsonResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from callcenter.models import MeetingRequest
from nadooit_website.models import Session
from django.core.exceptions import ObjectDoesNotExist
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@csrf_exempt
def create_meeting_request(request):
    print("create_meeting_request")
    try:
        if request.method == "POST":
            print("POST")
            session_id = request.POST.get("session_id")
            print("session_id", session_id)
            print("request", request)
            session = Session.objects.get(pk=session_id)
            user = request.user if request.user.is_authenticated else None

            # Check if there is an active request for the session
            try:
                active_request = MeetingRequest.objects.get(
                    session=session, status="pending"
                )
                print("active_request", active_request)
                return JsonResponse(
                    {
                        "status": "error",
                        "error": "An active request already exists",
                    },
                    content_type="application/json",
                )
            except MeetingRequest.DoesNotExist:
                print("no active_request")
                pass  # No active request found, continue creating a new one
            except MultipleObjectsReturned:
                print("Multiple active requests found")
                return JsonResponse(
                    {
                        "status": "error",
                        "error": "Multiple active requests found",
                    },
                    content_type="application/json",
                )

            print("create_meeting_request")
            # Create a new MeetingRequest
            meeting_request = MeetingRequest(session=session, user=user)
            meeting_request.save()

            # Send WebSocket message to notify the admin panel
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "notifications",
                {"type": "send_notification", "text": "New meeting request created"},
            )

            # Return a JSON response indicating success and the meeting status
            return JsonResponse(
                {
                    "status": "success",
                    "meeting_status": meeting_request.status,
                },
                content_type="application/json",
            )

        else:
            return JsonResponse(
                {
                    "status": "error",
                    "error": "Invalid request method",
                },
                content_type="application/json",
            )

    except ObjectDoesNotExist:
        print("Session not found")
        return JsonResponse(
            {
                "status": "error",
                "error": "Session not found",
            },
            content_type="application/json",
        )

    except Exception as e:
        return JsonResponse(
            {
                "status": "error",
                "error": str(e),
            },
            content_type="application/json",
        )
