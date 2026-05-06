from django.shortcuts import get_object_or_404, redirect, render
from .models import Event, EventSignup
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import EventCreateForm, EventUpdateForm, GuestEventSignupForm


class EventListView(ListView):
    model = Event
    template_name = 'localevents/event_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_events = context['event_list']

        created_events = Event.objects.none()
        signed_up_events = Event.objects.none()

        if self.request.user.is_authenticated:
            profile = getattr(self.request.user, 'profile', None)
            if profile is not None:
                created_events = Event.objects.filter(
                    event_organizers__organizer=profile,
                ).distinct()
                signed_up_events = Event.objects.filter(
                    event_signup__user_registrant=profile,
                ).distinct()

                grouped_event_ids = created_events.order_by().values_list('pk', flat=True).union(
                    signed_up_events.order_by().values_list('pk', flat=True)
                )
                all_events = all_events.exclude(pk__in=grouped_event_ids)

        context['created_events'] = created_events
        context['signed_up_events'] = signed_up_events
        context['all_events'] = all_events
        return context


class EventDetailView(DetailView):
    model = Event
    template_name = 'localevents/event_detail.html'
    pk_url_kwarg = 'event_id'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object

        signup_count = event.event_signup.count()
        is_full = signup_count >= event.event_capacity

        is_owner = False
        has_signed_up = False

        if self.request.user.is_authenticated:
            profile = getattr(self.request.user, 'profile', None)
            if profile is not None:
                is_owner = event.event_organizers.filter(organizer=profile).exists()
                has_signed_up = event.event_signup.filter(
                    user_registrant=profile,
                ).exists()

        context['signup_count'] = signup_count
        context['is_full'] = is_full
        context['is_owner'] = is_owner
        context['has_signed_up'] = has_signed_up
        context['can_signup'] = not is_owner and not is_full and not has_signed_up
        return context

class EventOrganizerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = False

    def test_func(self):
        profile = getattr(self.request.user, 'profile', None)
        return (
            profile is not None
            and profile.role == profile.ROLE_EVENT_ORGANIZER
        )

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return redirect('accounts:permission_denied')


class EventCreateView(EventOrganizerRequiredMixin, CreateView):
    model = Event
    form_class = EventCreateForm
    template_name = 'localevents/event_create.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        profile = self.request.user.profile
        self.object.event_organizers.get_or_create(organizer=profile)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['organizer_profile'] = getattr(self.request.user, 'profile', None)
        return context

class EventUpdateView(EventOrganizerRequiredMixin, UpdateView):
    model = Event
    form_class = EventUpdateForm
    template_name = 'localevents/event_update.html'
    pk_url_kwarg = 'event_id'

    def get_queryset(self):
        queryset = super().get_queryset()
        profile = getattr(self.request.user, 'profile', None)
        if profile is None:
            return queryset.none()
        return queryset.filter(event_organizers__organizer=profile).distinct()

    def form_valid(self, form):
        event = form.instance
        signup_count = event.event_signup.count()
        event.status = 'Full' if signup_count >= event.event_capacity else 'Available'
        return super().form_valid(form)

class EventSignupView(View):
    template_name = 'localevents/event_signup.html'

    def get(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        is_full = event.event_signup.count() >= event.event_capacity

        if is_full:
            return redirect(event.get_absolute_url())

        if request.user.is_authenticated:
            return redirect(event.get_absolute_url())

        if request.GET.get('from_detail') != '1':
            return redirect(event.get_absolute_url())

        request.session[f'event_signup_from_detail_{event_id}'] = True

        form = GuestEventSignupForm()
        return render(request, self.template_name, {
            'event': event,
            'form': form,
        })

    def post(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)

        signup_count = event.event_signup.count()
        is_full = signup_count >= event.event_capacity
        if is_full:
            return redirect(event.get_absolute_url())

        if request.user.is_authenticated:
            profile = getattr(request.user, 'profile', None)

            if profile is None:
                return redirect(event.get_absolute_url())

            is_owner = event.event_organizers.filter(organizer=profile).exists()
            if is_owner:
                return redirect(event.get_absolute_url())

            EventSignup.objects.get_or_create(
                event=event,
                user_registrant=profile,
                defaults={'new_registrant': ''},
            )
            return redirect(event.get_absolute_url())

        from_detail_session_key = f'event_signup_from_detail_{event_id}'
        if not request.session.get(from_detail_session_key, False):
            return redirect(event.get_absolute_url())

        form = GuestEventSignupForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {
                'event': event,
                'form': form,
            }, status=400)

        EventSignup.objects.create(
            event=event,
            new_registrant=form.cleaned_data['new_registrant'],
            user_registrant=None,
        )
        request.session.pop(from_detail_session_key, None)
        return redirect(event.get_absolute_url())
