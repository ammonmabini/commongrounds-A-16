from django.db import models
from django.urls import reverse

class EventType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('localevents:event_list', args=[str(self.name)])

    class Meta:
        ordering = ['name']

class Event(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(EventType, on_delete=models.CASCADE, 
                                 related_name='category')
    description = models.TextField()
    location = models.CharField(max_length=255)
    start_time = models.DateTimeField(null=False)
    end_time = models.DateTimeField(null=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}: {} '.format(self.title, self.description)
    
    def get_absolute_url(self):
        return reverse('localevents:event_detail', args=[str(self.pk)])

    class Meta:
        ordering = ['-created_on']
        unique_together = ['created_on', 'title']