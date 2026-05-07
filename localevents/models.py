from django.db import models
from django.urls import reverse


class EventType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('localevents:event_list')

    class Meta:
        ordering = ['name']


class Event(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(
        EventType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='category',
    )
    organizer = models.ManyToManyField(
        'accounts.Profile',
        through='EventOrganizer',
        through_fields=('event', 'organizer'),
        related_name='organizer',
        blank=True,
    )
    event_image = models.ImageField(upload_to='event_images/', null=False, blank=False)
    description = models.TextField()
    location = models.CharField(max_length=255)
    start_time = models.DateTimeField(null=False)
    end_time = models.DateTimeField(null=False)
    event_capacity = models.PositiveIntegerField()
    status = models.CharField(max_length=255, choices=[
        ('Available', 'Available'),
        ('Full', 'Full'),
        ('Done', 'Done'),
        ('Cancelled', 'Cancelled')
    ], default='Available')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}: {} '.format(self.title, self.description)

    def get_absolute_url(self):
        return reverse('localevents:event_detail', args=[str(self.pk)])

    class Meta:
        ordering = ['-created_on']
        unique_together = ['created_on', 'title']


class EventOrganizer(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='event_organizers',
    )
    organizer = models.ForeignKey(
        'accounts.Profile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='organized_event_links',
    )

    class Meta:
        unique_together = ['event', 'organizer']

    def __str__(self):
        if self.organizer is None:
            return f'{self.event.title}: removed organizer'
        return f'{self.event.title}: {self.organizer.display_name}'

class EventSignup(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='event_signup')
    user_registrant = models.ForeignKey(
        'accounts.Profile',
        on_delete=models.CASCADE,
        related_name='profile_signup',
        null=True,
        blank=True,
    )
    new_registrant = models.CharField(max_length=255, blank=True)


