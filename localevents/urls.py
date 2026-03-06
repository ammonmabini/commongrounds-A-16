from django.urls import include, path
from .views import EventDetailView, EventListView

urlpatterns = [
    path(
        'events',
        EventListView.as_view(),
        name='event_list'),
    path(
        'event/<int:event_id>',
        EventDetailView.as_view(),
        name='event_detail'),
]

app_name = 'localevents'
