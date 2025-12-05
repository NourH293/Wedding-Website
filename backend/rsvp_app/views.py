from rest_framework import views, status
from rest_framework.response import Response
from .models import Guest
from .serializers import GuestSerializer

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_list_or_404
from .models import Guest
import json


class GuestListView(views.APIView):
    """
    Handles GET requests to retrieve the full guest list, suitable for searching.
    """
    def get(self, request, *args, **kwargs):
        guests = Guest.objects.all()
        serializer = GuestSerializer(guests, many=True)
        return Response(serializer.data)

@csrf_exempt
def rsvp_update(request):
    """
    Handles PATCH requests to update the RSVP status for multiple guests
    within a family group.
    """
    if request.method != 'PATCH':
        return JsonResponse({"detail": "Method Not Allowed"}, status=405)

    try:
        # 1. Parse JSON payload from the request body
        data = json.loads(request.body)
        phoneNumber = data.get('phoneNumber')
        response_status = data.get('response') # Expected: 'Attending' or 'Declined'
        attending_count = data.get('attending_count')

        if not phoneNumber or not response_status:
            return JsonResponse({"detail": "Missing 'phoneNumber' or 'response' in payload."}, status=400)

        # Basic validation for the response status
        if response_status not in ['Attending', 'Declined']:
            return JsonResponse({"detail": "Invalid response status provided."}, status=400)

        # 2. Update the guests in the database
        updated_count = Guest.objects.filter(phoneNumber=phoneNumber).update(
            response=response_status,
            attending_count=attending_count,
        )

        if updated_count == 0:
            return JsonResponse({"detail": f"No guest was found with the provided Phone Number. Phone Number = {phoneNumber}"}, status=404)

        # 3. Return success response
        return JsonResponse({
            "message": "RSVP updated successfully.",
            "updated_count": updated_count,
            "response": response_status,
            "attending_count": attending_count,
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON in request body."}, status=400)
    except Exception as e:
        return JsonResponse({"detail": f"An unexpected error occurred: {str(e)}"}, status=500)