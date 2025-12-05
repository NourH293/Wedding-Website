from django.urls import path
from .rsvp_app import views

urlpatterns = [
    path('api/guests/', views.GuestListView.as_view(), name='guest-list'),
    path('api/rsvp/update/', views.rsvp_update, name='rsvp-update'),
]