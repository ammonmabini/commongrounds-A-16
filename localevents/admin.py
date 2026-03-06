from django.contrib import admin
from .models import Event, EventType


class EventAdmin(admin.ModelAdmin):
    model = Event
    search_fields = ('title', 'location')
    list_display = ('title', 'category', 'start_time', 'end_time')
    list_filter = ('category', 'start_time')
    fieldsets = [
        ('Details', {
            'fields': [
                ('title', 'category'),
                'description',
                'location',
                ('start_time', 'end_time'),
            ]
        }),
    ]


admin.site.register(EventType)
admin.site.register(Event, EventAdmin)
