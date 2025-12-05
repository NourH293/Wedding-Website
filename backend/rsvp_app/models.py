from django.db import models

class Guest(models.Model):
    """
    Represents a single wedding guest or member of a family group.
    """
    name = models.CharField(max_length=100, default="N/A")
    phoneNumber = models.CharField(max_length=50, primary_key=True, unique=True)
    maxGuests = models.CharField(max_length=50, default=1)
    attending_count = models.IntegerField(default=0)
    
    # RSVP Response: 'Pending', 'Attending', or 'Declined'
    response = models.CharField(
        max_length=10, 
        default='Pending',
        choices=[
            ('Pending', 'Pending'),
            ('Attending', 'Attending'),
            ('Declined', 'Declined'),
        ]
    )

    class Meta:
        # A simple unique constraint to prevent duplicate names/families if loaded improperly, though not strictly required
        # unique_together = ('name', 'response', 'attending_count')
        pass

    def __str__(self):
        return f"{self.name} - {self.response} - {self.attending_count}"