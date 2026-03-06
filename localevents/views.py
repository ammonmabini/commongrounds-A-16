from django.shortcuts import render
from django.http import HttpResponse
from django.tasks import Task
from .models import Event
from django.views.generic import DetailView, ListView


def index(request):
    return HttpResponse('Hello World! This came from the index view')


def event_list(request):
    event = Event.objects.all()
    return render(request, 'localevents/event_list.html', {
        "event": event,
    })


def event_detail(request, event_title):
    event = Event.objects.get(title=event_title)
    return render(request, 'localevents/event_detail.html', {
        "event": event,
    })


class EventListView(ListView):
    model = Event
    template_name = 'localevents/event_list.html'


class EventDetailView(DetailView):
    model = Event
    template_name = 'localevents/event_detail.html'
    pk_url_kwarg = 'event_id'
    context_object_name = 'event'
