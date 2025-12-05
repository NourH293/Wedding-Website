from rest_framework import serializers
from .models import Guest

class GuestSerializer(serializers.ModelSerializer):
    """
    Serializer for the Guest model to convert it to JSON format.
    """
    class Meta:
        model = Guest
        fields = ['name', 'phoneNumber', 'maxGuests', 'response', 'attending_count']
        read_only_fields = ['name', 'phoneNumber', 'maxGuests'] 